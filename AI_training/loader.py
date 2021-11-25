import numpy as np
import os
import pickle
from sklearn.utils import safe_mask
import torch
import torch.nn.functional as F
import torch.utils.data as data

import pdb

from torch.autograd import Variable

INPUT_DIM = 224
MAX_PIXEL_VAL = 255
MEAN = 58.09
STDDEV = 49.73

class Dataset(data.Dataset):
    def __init__(self, datadir, tear_type, use_gpu):
        super().__init__()
        self.use_gpu = use_gpu

        label_dict = {}
        self.paths = []
        abnormal_label_dict = {}
        
        if datadir[-1]=="/":
            datadir = datadir[:-1]
        self.datadir = datadir

        for i, line in enumerate(open(datadir+'-'+tear_type+'.csv').readlines()):
            line = line.strip().split(',')
            filename = line[0]
            label = line[1]
            label_dict[filename] = int(label)

        for i, line in enumerate(open(datadir+'-'+"abnormal"+'.csv').readlines()):
            line = line.strip().split(',')
            filename = line[0]
            label = line[1]
            abnormal_label_dict[filename] = int(label)

        for filename in os.listdir(os.path.join(datadir, "axial")):
            if filename.endswith(".npy"):
                self.paths.append(filename)
        
        self.labels = [label_dict[path.split(".")[0]] for path in self.paths]
        self.abnormal_labels = [abnormal_label_dict[path.split(".")[0]] for path in self.paths]

        if tear_type != "abnormal":
            temp_labels = [self.labels[i] for i in range(len(self.labels)) if self.abnormal_labels[i]==1]
            neg_weight = np.mean(temp_labels)
        else:
            neg_weight = np.mean(self.labels)
        
        self.weights = [neg_weight, 1 - neg_weight]

    def weighted_loss(self, prediction, target):
        weights_npy = np.array([self.weights[int(t[0])] for t in target.data])
        weights_tensor = torch.FloatTensor(weights_npy)
        if self.use_gpu:
            weights_tensor = weights_tensor.cuda()
        loss = F.binary_cross_entropy_with_logits(prediction, target, weight=Variable(weights_tensor))
        return loss

    def __getitem__(self, index):
        filename = self.paths[index]
        axi_scan = np.load(os.path.join(self.datadir, "axial", filename))
        cor_scan = np.load(os.path.join(self.datadir, "coronal", filename))
        sag_scan = np.load(os.path.join(self.datadir, "sagittal", filename))

        # axial
        pad = int((axi_scan.shape[2] - INPUT_DIM)/2)
        axi_scan = axi_scan[:,pad:-pad,pad:-pad]
        axi_scan = (axi_scan-np.min(axi_scan))/(np.max(axi_scan)-np.min(axi_scan))*MAX_PIXEL_VAL
        axi_scan = (axi_scan - MEAN) / STDDEV
        axi_scan = np.stack((axi_scan,)*3, axis=1)
        axi_scan_tensor = torch.FloatTensor(axi_scan)
        
        # sagittal
        pad = int((cor_scan.shape[2] - INPUT_DIM)/2)
        cor_scan = cor_scan[:,pad:-pad,pad:-pad]
        cor_scan = (cor_scan-np.min(cor_scan))/(np.max(cor_scan)-np.min(cor_scan))*MAX_PIXEL_VAL
        cor_scan = (cor_scan - MEAN) / STDDEV
        cor_scan = np.stack((cor_scan,)*3, axis=1)
        cor_scan_tensor = torch.FloatTensor(cor_scan)

        # coronal
        pad = int((sag_scan.shape[2] - INPUT_DIM)/2)
        sag_scan = sag_scan[:,pad:-pad,pad:-pad]
        sag_scan = (sag_scan-np.min(sag_scan))/(np.max(sag_scan)-np.min(sag_scan))*MAX_PIXEL_VAL
        sag_scan = (sag_scan - MEAN) / STDDEV
        sag_scan = np.stack((sag_scan,)*3, axis=1)
        sag_scan_tensor = torch.FloatTensor(sag_scan)

        label_tensor = torch.FloatTensor([self.labels[index]])

        return axi_scan_tensor,cor_scan_tensor,sag_scan_tensor, label_tensor, self.abnormal_labels[index]

    def __len__(self):
        return len(self.paths)

def load_data(task="acl", use_gpu=False):
    train_dir = "data/train"
    valid_dir = "data/valid"
    
    train_dataset = Dataset(train_dir, task, use_gpu)
    valid_dataset = Dataset(valid_dir, task, use_gpu)

    train_loader = data.DataLoader(train_dataset, batch_size=1, num_workers=1, shuffle=True)
    valid_loader = data.DataLoader(valid_dataset, batch_size=1, num_workers=1, shuffle=False)

    return train_loader, valid_loader