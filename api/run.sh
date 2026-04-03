hostname=$HOSTNAME
# echo $hostname

echo "start"
nohup python start.py > nohup.out 2>&1 &
