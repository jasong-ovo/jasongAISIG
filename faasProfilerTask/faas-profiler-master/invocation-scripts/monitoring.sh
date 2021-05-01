FAAS_ROOT="/home/gongjunchao/faas-profiler/faas-profiler-master"
FAAS_ROOT="/home/gongjunchao/faas-profiler/faas-profiler-master"
FAAS_ROOT="/home/gongjunchao/faas-profiler/faas-profiler-master"
time_stamp=$(date +%s%N | cut -b1-13)
systemd-cgtop > $FAAS_ROOT'/logs/systemd-cgtop_'$time_stamp'.txt'