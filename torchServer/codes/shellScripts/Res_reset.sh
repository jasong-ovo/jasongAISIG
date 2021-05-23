curl -X DELETE http://localhost:8081/models/resnet56
rm /home/gongjunchao/torchServer_task/model_store/resnet56.mar
torch-model-archiver --model-name resnet56 --version 1.0 --model-file ./serve/resnet56Model.py --serialized-file re56.pth --export-path model_store --extra-files ./serve/examples/image_classifier/index_to_name.json --handler /home/gongjunchao/torchServer_task/serve/Cifar10_resnet56_handler.py
curl -X POST "localhost:8081/models?url=resnet56.mar&batch_size=16&max_batch_delay=5000&initial_workers=1"

##curl http://localhost:8081/models/resnet56
##curl http://127.0.0.1:8080/predictions/resnet56 -T 001-8-ship.png
##curl -v -X PUT "http://localhost:8081/models/resnet56?max_worker=1&min_worker=1&synchronous=true"