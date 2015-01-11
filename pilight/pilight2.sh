#!/bin/sh
### BEGIN INIT INFO
# Provides:          pilight2
# Required-Start:    
# Required-Stop:    
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: 
# Description:       
### END INIT INFO

case "$1" in
start)
  /usr/local/sbin/pilight2.py &
;;
stop)
  ps -ef | grep "/usr/local/sbin/pilight2.py" | grep -v grep | awk '{print $2}' | xargs kill 
;;

status)
 if [ `ps -ef | grep "/usr/local/sbin/pilight2.py" | grep -v grep | wc -l` -gt 0 ]; then 
   echo "running"
 else
   echo "not running"
 fi 
;;
*)
        echo "Usage: $0 {start|stop|status}"
        exit 1
esac
