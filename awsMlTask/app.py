import time
import boto3

import torch
from pytorchcv.model_provider import get_model as ptcv_get_model
from torch.utils.data.dataloader import DataLoader

from utils import TestDataset


def handler(event, context):
    # global variables
    params = event
    result = {}
    model_index = 1
    model_names = ['resnet20_cifar10', 'resnet56_cifar10', 'resnet110_cifar10', 'resnet164bn_cifar10',
                   'resnet272bn_cifar10', 'resnet542bn_cifar10', 'resnet1001_cifar10', 'resnet1202_cifar10']
    model_name = model_names[model_index]

    # check device
    device = torch.device('cuda') if torch.cuda.is_available() and params['device'] == 'gpu' else torch.device('cpu')

    # connect to s3
    s3 = boto3.client('s3', aws_access_key_id="ASIAQVKPZROG2J2ESZO3", aws_secret_access_key="GHdTNxE/Z4c48wP0c4F50TaKT3G59Xu+vMpxgbA5",
                    aws_session_token="IQoJb3JpZ2luX2VjEPn//////////wEaCXVzLXdlc3QtMiJHMEUCIHCgvdjbj8S9S4D8gDh54bpLATSgPluc55CwqB+jtBqtAiEAi0VZtqpBqxLEohJ6foR9fMhb77ivekJz86K/Z8yOv34qrwIIcRAAGgwwNDU4MDEzNzY2NTMiDOugvxmX5mHGtj+NCSqMAsSuhgWkYxWfMJE1TgEpYRIehIpOuL0WayvOeOg+DMS15XLPCNKD69i1f5bOFcOzW9MbOZMA1yGYDV3TyS8XsliWQfU/JrEYCdeVZr3L83xqZe3+8/263a3vlYm2LF85sKzpq8SLlF4OTFxSku1UOQJZYJ1sgWligFZ33gM1gbzuDA/fC+Fe/u44Nmko23+ScJMYocdIwk2jQMdGMTv3tO4ZNKj2sYq3NcDUoHv8Z6/5kYpq+NkyGdi+GbF0XMnECp38OQWnK36pJIjt9wzLM4+jfKkP95s0Yx7k7fDx2/dj7cbDsiBJC3Lv+EWj8yy6MNyOewLe+D2g0SO94tGYe5F+0gAjR5EhlAVDrXYwm9mphAY6nQFRYIJBe/CLcJkzS/FqqFj+vp2shC2/OA5z/3iBm8xMjwOBBsrP6JD0dUSiHsIcuKrsGpAp23aOreiPfmmia/k+FfQTCPxD7jlmLOgLagqRbvE5sKumjyCSxnuA5+guoaW9/8zwQ7KPgrdhSXVLyKj3cXUWprv7HkJF/iivSNB1ZVmJlPc31Lp9ujyji+lpO5+V6sG8UIpqBT/ZGmKT")

    # start to prepare data
    start_prepare_data = int(time.time() * 1000)
    # step 1: download zipfile from s3
    with open ('/tmp/' + params['data_object'], 'wb') as f:
        s3.download_fileobj('east-access', 'cifar_batch_0.zip', f)
    # step 2: prepare dataset
    dataset = TestDataset('/tmp/' + params['data_object'])
    # step 3: prepare dataloader
    dataloader = DataLoader(dataset, batch_size=params['batch_size'])

    # start to prepare model
    start_prepare_model = int(time.time() * 1000)
    # step 1: prepare model structure
    model = ptcv_get_model(model_name, pretrained=False).to(device)
    # step 2: download model weight from s3   
    with open ('/tmp/' + model_name + '.pth', 'wb') as f:
        s3.download_fileobj('east-access', model_name + '.pth', f)
    # step 3: load weight
    model.load_state_dict(torch.load('/tmp/%s.pth' % model_name))

    # start to predict
    start_predict = int(time.time() * 1000)
    for _, data in enumerate(dataloader):
        img_paths, imgs = data
        imgs = imgs.to(device)

        out = model(imgs)
        _, pred = torch.max(out, 1)
        for i in range(len(img_paths)):
            result[img_paths[i]] = pred[i].item()

    # end time
    end_time = int(time.time() * 1000)

    result.update({
        'device': device == torch.device('cuda'),
        'prepare_data': start_prepare_model - start_prepare_data,
        'prepare_model': start_predict - start_prepare_model,
        'predict': end_time - start_predict
    })
    return result


if __name__ == "__main__":
    response = handler({"data_object": "cifar_batch_0.zip", "device": "gpu", "batch_size": 16}, 0)
    print(response)


