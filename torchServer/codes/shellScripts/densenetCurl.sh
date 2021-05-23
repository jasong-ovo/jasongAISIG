curl http://127.0.0.1:8080/predictions/densenet161_test -T kitten_small.jpg
for((i=0;i<2200;i++))
do  
    sleep 0.1
    curl http://127.0.0.1:8080/predictions/densenet161_test -T kitten_small.jpg&
done
