"""
Module for image classification default handler
"""
from ts.torch_handler.base_handler import BaseHandler
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import base64
import io
import logging
import os
from ts.utils.util import list_classes_from_module, load_label_mapping
import time

# from ts.torch_handler.vision_handler import VisionHandler
from ts.utils.util  import map_class_to_label
from ts.torch_handler.vision_handler import VisionHandler

logger = logging.getLogger(__name__)

class ImageClassifier(VisionHandler):
    """
    ImageClassifier handler class. This handler takes an image
    and returns the name of object in that image.
    """

    topk = 5
    # These are the standard Imagenet dimensions
    # and statistics
    image_processing = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

    def set_max_result_classes(self, topk):
        self.topk = topk

    def get_max_result_classes(self):
        return self.topk

    def postprocess(self, data):
        ps = F.softmax(data, dim=1)
        probs, classes = torch.topk(ps, self.topk, dim=1)
        probs = probs.tolist()
        classes = classes.tolist()
        # return map_class_to_label(probs, self.mapping, classes)
        return [i for i in range(len(probs))]
    
    def preprocess(self, data):
        """The preprocess function of MNIST program converts the input data to a float tensor

        Args:
            data (List): Input data from the request is in the form of a Tensor

        Returns:
            list : The preprocess function returns the input image as a list of float tensors.
        """
        images = []
        # print(data)
        # f = open("/home/gongjunchao/torchServer_task/serve/record.zip", mode='w')
        # f.write(str(data[0]["body"]))
        # print(data.keys())


        for row in data:
            # print(row)
            # Compat layer: normally the envelope should just return the data
            # directly, but older versions of Torchserve didn't have envelope.
            self.sum = self.sum + 1
            image = row.get("data") or row.get("body")
            if isinstance(image, str):
                # if the image is a string of bytesarray.
                image = base64.b64decode(image)

            # If the image is sent as bytesarray
            if isinstance(image, (bytearray, bytes)):
                image = Image.open(io.BytesIO(image))
                image = self.image_processing(image)
            else:
                # if the image is a list
                image = torch.FloatTensor(image)

            images.append(image)

        return torch.stack(images).to(self.device)

    
    ## measure time
    def __init__(self):
        self.model = None
        self.mapping = None
        self.device = None
        self.initialized = False
        self.context = None
        self.manifest = None
        self.map_location = None
        self.explain = False
        self.target = 0
        self.initTime = 0
        self.loadModelTime = 0
        self.modelToDeviceTime = 0
        self.handleTime = 0
        self.preprocessTime = 0
        self.predictionTime = 0
        self.postprocessTime = 0
        self.sum = 0

    def initialize(self, context):
        """Initialize function loads the model.pt file and initialized the model object.
	   First try to load torchscript else load eager mode state_dict based model.

        Args:
            context (context): It is a JSON Object containing information
            pertaining to the model artifacts parameters.

        Raises:
            RuntimeError: Raises the Runtime error when the model.py is missing

        """
        start_init_time = time.time()
        properties = context.system_properties
        self.map_location = "cuda" if torch.cuda.is_available() and properties.get("gpu_id") else "cpu"
        self.device = torch.device(
            self.map_location + ":" + str(properties.get("gpu_id"))
            if torch.cuda.is_available() and properties.get("gpu_id")
            else self.map_location
        )
        ############
        # self.device = 'gpu'
        ###########
        self.manifest = context.manifest

        model_dir = properties.get("model_dir")
        model_pt_path = None
        if "serializedFile" in self.manifest["model"]:
            serialized_file = self.manifest["model"]["serializedFile"]
            model_pt_path = os.path.join(model_dir, serialized_file)

        # model def file
        model_file = self.manifest["model"].get("modelFile", "")

        if model_file:
            logger.debug("Loading eager model")
            start_loadmodel = time.time()
            self.model = self._load_pickled_model(model_dir, model_file, model_pt_path)
            end_loadmodel = time.time()
            start_2device = time.time()
            self.model.to(self.device)
            end_2device = time.time()
        else:
            logger.debug("Loading torchscript model")
            if not os.path.isfile(model_pt_path):
                raise RuntimeError("Missing the model.pt file")

            self.model = self._load_torchscript_model(model_pt_path)

        self.model.eval()

        logger.debug('Model file %s loaded successfully', model_pt_path)

        # Load class mapping for classifiers
        mapping_file_path = os.path.join(model_dir, "index_to_name.json")
        self.mapping = load_label_mapping(mapping_file_path)

        self.initialized = True
        end_init_time = time.time()
        self.initTime = end_init_time - start_init_time
        self.loadModelTime = end_loadmodel - start_loadmodel
        self.modelToDeviceTime = end_2device - start_2device

    def handle(self, data, context):
        """Entry point for default handler. It takes the data from the input request and returns
           the predicted outcome for the input.

        Args:
            data (list): The input data that needs to be made a prediction request on.
            context (Context): It is a JSON Object containing information pertaining to
                               the model artefacts parameters.

        Returns:
            list : Returns a list of dictionary with the predicted response.
        """

        # It can be used for pre or post processing if needed as additional request
        # information is available in context
        start_time = time.time()

        self.context = context
        metrics = self.context.metrics

        statr_pre_time = time.time()
        data_preprocess = self.preprocess(data)
        end_pre_time = time.time()

        if not self._is_explain():
            start_prediction_time = time.time()
            output = self.inference(data_preprocess)
            end_prediction_time = time.time()
            start_post_time = time.time()
            output = self.postprocess(output)
            end_post_time = time.time()
        else :
            output = self.explain_handle(data_preprocess, data)

        stop_time = time.time()
        tmpHandleTime = stop_time - start_time
        tmpPreprocessTime = end_pre_time - statr_pre_time
        tmpPredictionTime = end_prediction_time - start_prediction_time
        tmpPostprocessTime = end_post_time - start_post_time
        self.handleTime = self.handleTime + tmpHandleTime
        self.preprocessTime = self.preprocessTime + tmpPreprocessTime
        self.predictionTime = self.predictionTime + tmpPredictionTime
        self.postprocessTime =  self.postprocessTime + tmpPostprocessTime
        # metrics.add_time('HandlerTime', round((stop_time - start_time) * 1000, 2), None, 'ms')
        #单个输入
        outputSingle = [{
            "init":{
                "init time": self.initTime ,
                "load model time": self.loadModelTime ,
                "model to device time": self.modelToDeviceTime
        },
            "handle":{
                "handle time": self.handleTime ,
                "preprocess time": self.preprocessTime ,
                "prediction time": self.predictionTime ,
                "postprocess time": self.postprocessTime
        },
            "device": str(self.device),
            "sum": self.sum
            }]
        for i in range(len(output)):
            output[i] = outputSingle
        return output