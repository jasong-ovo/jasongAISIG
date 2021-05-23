curl http://127.0.0.1:8080/predictions/resnet56 -T 001-8-ship.png
for((i=0;i<2200;i++))
do
    sleep 0.1
    curl http://127.0.0.1:8080/predictions/resnet56 -T 001-8-ship.png &
done