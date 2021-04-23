import os
import zipfile
import copy

import numpy as np
import torch
from PIL import Image
from minio import Minio
from minio.error import S3Error
from torch.utils import data
from torch.utils.data.dataset import Dataset


class TestDataset(Dataset):
    def __init__(self, path):
        extract_zipfile(path)

        self.img_prefix = path[:-4] + '/'
        self.images = os.listdir(self.img_prefix)

        ##debug
        

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        img_path = self.img_prefix + self.images[index]
        image = Image.open(img_path)
        image = torch.tensor(np.array(image))
        image = image.permute(2, 0, 1).float() / 255
        return img_path, image
    

def trainer(net, dataloader, loss_function, optimizer, device='cpu', epochs = 20):
    """
    train the network
    : model name
    : dataloader
    : loss_function
    : optimizer
    : devcie
    : epochs
    """
    for epoch in range(epochs):
        running_loss = 0.0
        print(epochs)
        for i,data in enumerate(dataloader,0):
            # get the inputs
            img_paths, imgs = data
            imgs =  imgs.to(device)
            labels = []
            # labels_tensor = []
            # help_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for img_path in img_paths:
                labels.append(int(img_path[14:-4].split('-')[1]))
            labels = torch.tensor(labels, dtype=int, device=device)
            
            # for j in labels:
            #     help_list_sub = copy.deepcopy(help_list)
            #     help_list_sub[int(labels[int(j)])] = 1
            #     labels_tensor.append(help_list_sub)
            # labels_tensor = torch.tensor(labels_tensor, dtype=float, device=device)

            # zero the parameter gradients
            optimizer.zero_grad()#gradients are eliminated , params are saved

            # forward + backward + optimize
            outputs = net(imgs)
            loss = loss_function(outputs, labels)
            loss.backward() #compute gradients
            optimizer.step() #params learn the gradients

            # print statistics
            running_loss += loss.item()
            if i % 2000 == 1999:    # print every 2000 mini-batches
                print('[%d, %5d] loss: %.3f' % (epoch + 1, i + 1, running_loss / 2000))
                running_loss = 0.0

    print('Finished Training')



def extract_zipfile(path):
    """
    extract zipfile
    :param path: the path of the zipfile. The file must exist and end with '.zip'
    :return: nothing
    """
    try:
        assert path[-4:] == '.zip'
        extract_dir = path[:-4]

        with zipfile.ZipFile(path, 'r') as zip_ref:
            if not os.path.exists(extract_dir):
                os.mkdir(extract_dir)
            zip_ref.extractall(extract_dir)

    except (IndexError, AssertionError, FileNotFoundError):
        print('something wrong with the test dataset path!')
        exit(1)


def download_from_minio(bucket_name, object_name):
    if os.path.exists(object_name):
        print('%s already exists locally!' % object_name)
        return
    try:
        minio_host = '10.105.149.213'
        minio_port = 9000
        client = Minio(
            '%s:%s' % (minio_host, minio_port),
            access_key='AKIAIOSFODNN7EXAMPLE',
            secret_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            secure=False
        )

        found = client.bucket_exists(bucket_name)
        if not found:
            print('bucket %s not exists' % bucket_name)
            exit(1)

        client.fget_object(bucket_name, object_name, object_name)
        print('prepare %s from bucket %s successfully' % (object_name, bucket_name))
    except S3Error:
        print('something wrong with MinIO storage!')
        exit(-1)
