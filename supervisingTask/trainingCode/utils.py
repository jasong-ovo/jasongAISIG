import os
import zipfile
import copy
import re

import numpy as np
import torch
from PIL import Image
from minio import Minio
from minio.error import S3Error
from torch.utils import data
from torch.utils.data.dataset import Dataset


class CifarDataset(Dataset):
    def __init__(self, path):
        self.images = []
        for file in os.listdir(path):
            if re.match('cifar',file):
                self.img_prefix = './' + file + '/'
                imgs = os.listdir(self.img_prefix)
                imgs = [self.img_prefix + i for i in os.listdir(self.img_prefix)]
                self.images = self.images + imgs
        
    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        img_path = self.images[index]
        object_id = re.findall('-(.*)-', img_path)
        label = int(object_id[0])

        image = Image.open(img_path)
        image = torch.tensor(np.array(image))
        image = image.permute(2, 0, 1).float() / 255
        return label, image
    

def trainer(net, dataloader, loss_function, optimizer, device='gpu', epochs = 20):
    """
    train the network
    : model name
    : dataloader
    : loss_function
    : optimizer
    : devcie
    : epochs
    """
    print("%d epochs' training"%(epochs))
    for epoch in range(epochs):
        training_accuracy = 0.0
        for i,data in enumerate(dataloader,0):
            # get the inputs
            labels, imgs = data
            imgs =  imgs.to(device)
            labels = torch.tensor(labels)
            labels = labels.to(device)
            
            # zero the parameter gradients
            optimizer.zero_grad()#gradients are eliminated , params are saved

            # forward + backward + optimize
            outputs = net(imgs)
            loss = loss_function(outputs, labels)
            loss.backward() #compute gradients
            optimizer.step() #params learn the gradients
        
            # deal the data
            prediction = torch.max(outputs, 1).indices
            prediction = prediction.to(device)
            acc = torch.mean(torch.eq(prediction, labels).type(torch.FloatTensor))
            training_accuracy = training_accuracy + acc.item() * labels.size(0)


        # print statistics
        data_size = len(dataloader.dataset)
        print("training accuracy for %d epoch: %f"%(epoch, training_accuracy/data_size))


    print('Finished Training')






