torchserve --stop
rm /home/gongjunchao/torchServer_task/model_store/*
torch-model-archiver --model-name densenet161_test --version 1.0 --model-file ./serve/examples/image_classifier/densenet_161/model.py --serialized-file densenet161-8d451a50.pth --export-path model_store --extra-files ./serve/examples/image_classifier/index_to_name.json --handler /home/gongjunchao/torchServer_task/serve/eg_handler.py
torchserve --start --ncs --model-store model_store --models densenet161_test.mar
