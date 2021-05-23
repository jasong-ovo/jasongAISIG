curl -X DELETE http://localhost:8081/models/densenet161_test
rm /home/gongjunchao/torchServer_task/model_store/densenet161_test.mar
torch-model-archiver --model-name densenet161_test --version 1.0 --model-file ./serve/examples/image_classifier/densenet_161/model.py --serialized-file densenet161-8d451a50.pth --export-path model_store --extra-files ./serve/examples/image_classifier/index_to_name.json --handler /home/gongjunchao/torchServer_task/serve/ImaNet_densenet161_handler.py
curl -X POST "localhost:8081/models?url=densenet161_test.mar&batch_size=16&max_batch_delay=5000&initial_workers=1"

##curl http://localhost:8081/models/densenet161_test  ##查看节点状态
##curl http://127.0.0.1:8080/predictions/densenet161_test -T 001-8-ship.png ##发图片
##curl -v -X PUT "http://localhost:8081/models/densenet161_test?max_worker=1&min_worker=1&synchronous=true" ##设置worker数量
