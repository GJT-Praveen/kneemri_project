import numpy as np
import os
import pickle
import sys

import torch
import torch.nn.functional as F
import torch.utils.data as data
from torch.autograd import Variable

from model import TripleMRNet

INPUT_DIM = 224
MAX_PIXEL_VAL = 255
MEAN = 58.09
STDDEV = 49.73


def get_study(axial_path, sagit_path, coron_path):
    axi_scan = np.load(axial_path)
    cor_scan = np.load(coron_path)
    sag_scan = np.load(sagit_path)

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
    sag_scan_tensor = torch.FloatTensor(cor_scan)

    # coronal
    pad = int((sag_scan.shape[2] - INPUT_DIM)/2)
    sag_scan = sag_scan[:,pad:-pad,pad:-pad]
    sag_scan = (sag_scan-np.min(sag_scan))/(np.max(sag_scan)-np.min(sag_scan))*MAX_PIXEL_VAL
    sag_scan = (sag_scan - MEAN) / STDDEV
    sag_scan = np.stack((sag_scan,)*3, axis=1)
    cor_scan_tensor = torch.FloatTensor(sag_scan)
    
    return {"axial": axi_scan_tensor,
            "coron": cor_scan_tensor,
            "sagit": sag_scan_tensor}


def get_prediction(model, tensors, abnormality_prior=None):
    axi_scan = tensors["axial"].cuda()
    cor_scan = tensors["coron"].cuda()
    sag_scan = tensors["sagit"].cuda()

    axi_scan = Variable(axi_scan)
    cor_scan = Variable(cor_scan)
    sag_scan = Variable(sag_scan)

    logit = model.forward(axi_scan, cor_scan, sag_scan)
    pred = torch.sigmoid(logit)
    pred_npy = pred.data.cpu().numpy()[0][0]
    
    if abnormality_prior:
        pred_npy = pred_npy * abnormality_prior

    return pred_npy


if __name__=="__main__":
    input_csv_path = sys.argv[1]
    preds_csv_path = sys.argv[2]

    # Assuming that the input csv has all three views for each ID.
    # And that entries are sorted by ID.
    views = []
    for i, fpath in enumerate(open(input_csv_path).readlines()):
        if "axial" in fpath:
            axial_path = fpath.strip()
        elif "sagittal" in fpath:
            sagit_path = fpath.strip()
        elif "coronal" in fpath:
            coron_path = fpath.strip()
        if i%3==2:
            views.append(get_study(axial_path, sagit_path, coron_path))


    # Loading all models
    abnormal_model_path = "models/abnormal_model_val_auc_0.9482_train_auc_0.9571_val_loss_0.1039_train_loss_0.0855_epoch_10"
    acl_model_path = "models/acl_model_val_auc_0.9386_train_auc_0.9691_val_loss_0.1672_train_loss_0.0888_epoch_74"
    meniscal_model_path = "models/meniscus_model_val_auc_0.8102_train_auc_0.9167_val_loss_0.2604_train_loss_0.1888_epoch_21"


    # Getting predictions
    abnormality = []
    acl_tear = []
    meniscal_tear = []
    
    abnormal_model = TripleMRNet(backbone="alexnet", training=False)
    state_dict = torch.load(abnormal_model_path)
    abnormal_model.load_state_dict(state_dict)
    abnormal_model.cuda()
    abnormal_model.eval()
    for study in views:
        abnormality.append(get_prediction(
                abnormal_model,
                study,
                abnormality_prior=None))
    del abnormal_model

    acl_model = TripleMRNet(backbone="alexnet", training=False)
    state_dict = torch.load(acl_model_path)
    acl_model.load_state_dict(state_dict)
    acl_model.cuda()
    acl_model.eval()
    for idx,study in enumerate(views):
        acl_tear.append(get_prediction(
                acl_model,
                study,
                abnormality_prior=abnormality[idx]))
    del acl_model

    meniscal_model = TripleMRNet(backbone="alexnet", training=False)
    state_dict = torch.load(meniscal_model_path)
    meniscal_model.load_state_dict(state_dict)
    meniscal_model.cuda()
    meniscal_model.eval()
    for idx,study in enumerate(views):
        meniscal_tear.append(get_prediction(
                meniscal_model,
                study,
                abnormality_prior=abnormality[idx]))
    del meniscal_model
    

    with open(preds_csv_path, "w") as csv_file:        
        for i in range(len(abnormality)):
            csv_file.write(",".join(
                [str(abnormality[i]), str(acl_tear[i]), str(meniscal_tear[i])]))
            csv_file.write("\n")