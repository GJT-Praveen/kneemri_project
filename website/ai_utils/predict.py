import os
import numpy as np
import torch
from torch.autograd import Variable
from website.ai_utils.model import TripleMRNet


def scan_loader():

    INPUT_DIM = 224
    MAX_PIXEL_VAL = 255
    MEAN = 58.09
    STDDEV = 49.73

    data_dir=r'website\ai_utils\uploads'

    axi_scan=np.load(os.path.join(data_dir,'axi_scan.npy'),allow_pickle=True)
    cor_scan=np.load(os.path.join(data_dir,'cor_scan.npy'),allow_pickle=True)
    sag_scan=np.load(os.path.join(data_dir,'sag_scan.npy'),allow_pickle=True)

    pad = int((axi_scan.shape[2] - INPUT_DIM)/2)
    axi_scan = axi_scan[:,pad:-pad,pad:-pad]
    axi_scan = (axi_scan-np.min(axi_scan))/(np.max(axi_scan)-np.min(axi_scan))*MAX_PIXEL_VAL
    axi_scan = (axi_scan - MEAN) / STDDEV
    axi_scan = np.stack((axi_scan,)*3, axis=1)
    axi_scan_tensor = torch.FloatTensor(axi_scan)

    cor_scan = cor_scan[:,pad:-pad,pad:-pad]
    cor_scan = (cor_scan-np.min(cor_scan))/(np.max(cor_scan)-np.min(cor_scan))*MAX_PIXEL_VAL
    cor_scan = (cor_scan - MEAN) / STDDEV
    cor_scan = np.stack((cor_scan,)*3, axis=1)
    cor_scan_tensor = torch.FloatTensor(cor_scan)

    sag_scan = sag_scan[:,pad:-pad,pad:-pad]
    sag_scan = (sag_scan-np.min(sag_scan))/(np.max(sag_scan)-np.min(sag_scan))*MAX_PIXEL_VAL
    sag_scan = (sag_scan - MEAN) / STDDEV
    sag_scan = np.stack((sag_scan,)*3, axis=1)
    sag_scan_tensor = torch.FloatTensor(sag_scan)
    return axi_scan_tensor,cor_scan_tensor,sag_scan_tensor

def get_prediction(model,task,axi_scan,cor_scan,sag_scan):

    if torch.cuda.is_available():
        model.cuda()
    model.eval()
            
    logit=model.forward(axi_scan,cor_scan,sag_scan)

    pred=torch.sigmoid(logit)
    pred_npy=pred.data.cpu().numpy()[0][0]

    if task=='abnormal':
        threshold=0.25
    else:
        threshold=0.5

    if pred_npy>threshold:
        return 'Yes'
    else:
        return 'No'

def predict_diagnosis():
    abnormal_path=r'website\ai_utils\ai_model_dicts\abnormal_model'
    acl_path=r'website\ai_utils\ai_model_dicts\acl_model'
    meniscus_path=r'website\ai_utils\ai_model_dicts\meniscus_model'

    model_paths={'abnormal':abnormal_path,'acl':acl_path,'meniscus':meniscus_path}
    predictions=[]
    axi_scan,cor_scan,sag_scan=scan_loader()

    if torch.cuda.is_available():
        axi_scan,cor_scan,sag_scan=axi_scan.cuda(),cor_scan.cuda(),sag_scan.cuda()
        axi_scan,cor_scan,sag_scan=Variable(axi_scan),Variable(cor_scan),Variable(sag_scan)

    for item in model_paths.items():
        diagnosis,path=item
        use_gpu=1

        model=TripleMRNet(backbone='alexnet')
        state_dict=torch.load(path,map_location=(None if use_gpu else 'cpu'))
        model.load_state_dict(state_dict)

        predictions.append(get_prediction(model,diagnosis,axi_scan,cor_scan,sag_scan))

        del model
        torch.cuda.empty_cache()

    print(predictions[0])
    print(predictions[1])
    print(predictions[2])
    
    return predictions[0],predictions[1],predictions[2]




    