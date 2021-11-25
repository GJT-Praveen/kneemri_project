import torch
from torch.autograd import Variable
import os
import numpy as np

def converter():
    abnormal_path=r'website\ai_utils\ai_models\abnormal_model_val_auc_0.9482_train_auc_0.9571_val_loss_0.1039_train_loss_0.0855_epoch_10.pth'
    acl_path=r'website\ai_utils\ai_models\acl_model_val_auc_0.9386_train_auc_0.9691_val_loss_0.1672_train_loss_0.0888_epoch_74.pth'
    meniscus_path=r'website\ai_utils\ai_models\meniscus_model_val_auc_0.8102_train_auc_0.9167_val_loss_0.2604_train_loss_0.1888_epoch_21.pth'

    model1=torch.load(abnormal_path)
    torch.save(model1.state_dict(),r'website\ai_utils\ai_model_dicts\abnormal_model')
    model2=torch.load(acl_path)
    torch.save(model2.state_dict(),r'website\ai_utils\ai_model_dicts\acl_model')
    model3=torch.load(meniscus_path)
    torch.save(model3.state_dict(),r'website\ai_utils\ai_model_dicts\meniscus_model')

def scan_loader():

    INPUT_DIM = 224
    MAX_PIXEL_VAL = 255
    MEAN = 58.09
    STDDEV = 49.73

    data_dir=r'website\ai_utils\uploads'
    axi_scan=np.load(os.path.join(data_dir,'axi_scan.npy'))
    cor_scan=np.load(os.path.join(data_dir,'cor_scan.npy'))
    sag_scan=np.load(os.path.join(data_dir,'sag_scan.npy'))

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

def get_prediction(pred_raw,task):
    if task=='abnormal':
        threshold=0.25
    else:
        threshold=0.5
    if pred_raw>threshold:
        return 'yes'
    else:
        return 'no'

def predict_diagnosis():
    abnormal_path=r'website\ai_utils\ai_models\abnormal_model_val_auc_0.9482_train_auc_0.9571_val_loss_0.1039_train_loss_0.0855_epoch_10.pth'
    acl_path=r'website\ai_utils\ai_models\acl_model_val_auc_0.9386_train_auc_0.9691_val_loss_0.1672_train_loss_0.0888_epoch_74.pth'
    meniscus_path=r'website\ai_utils\ai_models\meniscus_model_val_auc_0.8102_train_auc_0.9167_val_loss_0.2604_train_loss_0.1888_epoch_21.pth'

    model_paths={'abnormal':abnormal_path,'acl':acl_path,'meniscus':meniscus_path}
    predictions=[]
    axi_scan,cor_scan,sag_scan=scan_loader()

    if torch.cuda.is_available():
        axi_scan,cor_scan,sag_scan=axi_scan.cuda(),cor_scan.cuda(),sag_scan.cuda()
        axi_scan,cor_scan,sag_scan=Variable(axi_scan),Variable(cor_scan),Variable(sag_scan)

    for item in model_paths.items():
        path=item[1]
        use_gpu=1
        model=torch.load(path,map_location=(None if use_gpu else 'cpu'))

        if torch.cuda.is_available():
            model.cuda()
        model.eval()
            
        logit=model.forward(axi_scan,cor_scan,sag_scan)

        pred=torch.sigmoid(logit)
        pred_npy=pred.data.cpu().numpy()[0][0]
        predictions.append(get_prediction(pred_npy,item[0]))
        del model
        torch.cuda.empty_cache()
    
    return predictions[0],predictions[1],predictions[2]


