import os
import zipfile

import numpy as np
import torch
from PIL import Image
# from minio import Minio
# from minio.error import S3Error
from torch.utils.data.dataset import Dataset


class TestDataset(Dataset):
    def __init__(self, path):
        extract_zipfile(path)

        self.img_prefix = path[:-4] + '/'
        self.images = os.listdir(self.img_prefix)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        img_path = self.img_prefix + self.images[index]
        image = Image.open(img_path)
        image = torch.tensor(np.array(image))
        image = image.permute(2, 0, 1).float() / 255
        return img_path, image


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