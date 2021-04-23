from utils import TestDataset, extract_zipfile, download_from_minio, trainer
import torch
from torch.utils.data.dataloader import DataLoader
import time
import torch.optim as optim
import torch.nn as nn

def main(params):
    #global variables
    result = {}
    model_index = 0
    model_names = ['vgg11_cifar10']
    model_name = model_names[model_index]

    # check device
    device = torch.device('cuda') if torch.cuda.is_available() and params['device'] == 'gpu' else torch.device('cpu')
    device = 'cuda'
    print(device)
    # start to prepare data
    start_prepare_data = int(time.time() * 1000)
    # step 1: download zipfile from minio
    # debug:download_from_minio('data', params['data_object'])
    # step 2: prepare dataset
    dataset = TestDataset(params['data_object'])
    # step 3: prepare dataloader
    dataloader = DataLoader(dataset, batch_size=params['batch_size'])

    # start to prepare model
    start_prepare_model = int(time.time() * 1000)
    # step 1: download model weight from minio
    # debug: download_from_minio('models', '%s.pth' % model_name)
    # step 2: load model
    model = torch.load('%s.pth' % model_name)
    model = model.to(device)
    model.train()

    # start to train
    start_train = int(time.time() * 1000)
    # step 1: define loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)
    # step 2: train the network
    trainer(model, dataloader, criterion, optimizer, device)

    end_time = int(time.time() * 1000)

    result.update({
        'device': device == torch.device('cuda'),
        'prepare_data': start_prepare_model - start_prepare_data,
        'prepare_model': start_train - start_prepare_model,
        'predict': end_time - start_train
    })
    return result

if __name__ == "__main__":
    response = main({"data_object": "cifar_batch_1.zip", "device": "gpu", "batch_size": 16})
    print(response)
