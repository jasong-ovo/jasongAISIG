pid=`ps -ef|grep gongjun.*nvidia-smi|awk 'NR==1{print $2}'`
echo $pid
kill -9 $pid
