import argparse
import json
import numpy as np
import os
import torch

from datetime import datetime
from pathlib import Path
from sklearn import metrics

from evaluate import run_model
from loader import load_data
from model import TripleMRNet

def get_lr(optimizer):
    for param_group in optimizer.param_groups:
        return param_group['lr']

def train(rundir, task, backbone, epochs, learning_rate, use_gpu,max_patience,
        abnormal_model_path=None):
    train_loader, valid_loader = load_data(task, use_gpu)
    max_epoch = 0
    best_val_loss=float('inf')
    model = TripleMRNet(backbone=backbone)

    for dirpath, dirnames, files in os.walk(f'{args.rundir}/models'):
        if not files:
            break
        model_path = None
        
        for fname in files:
            if task in fname:
                ep = int(fname[-2:-1])
                if ep >= max_epoch:
                    max_epoch = ep
                    best_val_loss=float(fname[-37:-31])
                    model_path = os.path.join(dirpath, fname)

        if model_path:
            state_dict=torch.load(model_path,map_location=(None if use_gpu else 'cpu'))
            model.load_state_dict(state_dict)
            print(f"Found a model saved on {max_epoch}th epoch and resuming training")

    optimizer = torch.optim.Adam(model.parameters(), learning_rate, weight_decay=.01)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=3, factor=.3, threshold=1e-4)

    if task!='abnormal':
        best_val_loss = float('inf')

    start_time = datetime.now()

    epoch = max_epoch
    current_lr=get_lr(optimizer)
    iteration_change_loss = 0

    if torch.cuda.is_available():
        model = model.cuda()

    while epoch < epochs:
        change = datetime.now() - start_time
        print(f'starting epoch {epoch+1}. with learning_rate = {current_lr}. time passed: {str(change)}')

        train_loss, train_auc, _, _ = run_model(
                model, train_loader, train=True, optimizer=optimizer,
                abnormal_model_path=abnormal_model_path)

        print(f'train loss: {train_loss:0.4f}')
        print(f'train AUC: {train_auc:0.4f}')

        val_loss, val_auc, _, _ = run_model(model, valid_loader,
                abnormal_model_path=abnormal_model_path)
        
        print(f'valid loss: {val_loss:0.4f}')
        print(f'valid AUC: {val_auc:0.4f}')

        iteration_change_loss += 1

        scheduler.step(val_loss)            

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            iteration_change_loss=0
            if epoch<10:
                file_name = f'{task}_model_val_auc_{val_auc:0.4f}_train_auc_{train_auc:0.4f}_val_loss_{val_loss:0.4f}_train_loss_{train_loss:0.4f}_epoch_0{epoch+1}'
            else:
                file_name = f'{task}_model_val_auc_{val_auc:0.4f}_train_auc_{train_auc:0.4f}_val_loss_{val_loss:0.4f}_train_loss_{train_loss:0.4f}_epoch_{epoch+1}'
            save_path = f'{Path(rundir)}/models/{file_name}'
            torch.save(model.state_dict(), save_path)
        
        if iteration_change_loss == max_patience:
            print('Early stopping after {0} epochs without the decrease of the val loss'.
                  format(iteration_change_loss))
            break

        epoch += 1

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rundir', type=str, required=True)
    parser.add_argument('--task', type=str, required=True)
    parser.add_argument('--seed', default=42, type=int)
    parser.add_argument('--gpu', action='store_true')
    parser.add_argument('--learning_rate', default=9e-07, type=float)
    parser.add_argument('--weight_decay', default=0.01, type=float)
    parser.add_argument('--epochs', default=75, type=int)
    parser.add_argument('--max_patience', default=5, type=int)
    parser.add_argument('--factor', default=0.3, type=float)
    parser.add_argument('--backbone', default="alexnet", type=str)
    parser.add_argument('--abnormal_model', default=None, type=str)
    return parser

if __name__ == '__main__':
    args = get_parser().parse_args()
    
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if args.gpu:
        torch.cuda.manual_seed_all(args.seed)

    os.makedirs(args.rundir, exist_ok=True)
    
    with open(Path(args.rundir) / 'args.json', 'w') as out:
        json.dump(vars(args), out, indent=4)

    train(args.rundir, args.task, args.backbone, args.epochs, args.learning_rate, 1,args.max_patience, abnormal_model_path=args.abnormal_model)