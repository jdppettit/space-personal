#!/bin/bash

# Source function library
. /etc/init.d/functions

SPACE_PATH=/srv/space
SPACE_PIDFILE=/var/run/space.pid
PROG=gunicorn
CONFIG_PATH=/srv/space/conf.d/gunicorn.conf.py

start () {
    echo -e "Starting Space:"
    cd $SPACE_PATH
    gunicorn --config $CONFIG_PATH space:app
    RETVAL=$?
    echo -n
    [ $RETVAL = 0 ] && echo -e '[\e[32m OK \e[m]'
    return $RETVAL
}

stop () {
    echo -e "Stopping Space:"
    killproc -p ${SPACE_PIDFILE} ${PROG} -QUIT
    RETVAL=$?
    echo
    [ $RETVAL = 0 ] && rm -f ${SPACE_PIDFILE} 

}

restart () {
    echo -e "Restarting space."
    echo -e "Stopping Space:"
    killproc -p ${SPACE_PIDFILE} ${PROG} -QUIT
    RETVAL=$?
    echo -e "Starting Space:"
    cd $SPACE_PATH
    gunicorn --config $CONFIG_PATH space:app
    RETVAL=$?
    echo -n
    [ $RETVAL = 0 ] && echo -e '[\e[32m OK \e[m]'
    return $RETVAL
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    *)
        echo -e "Usage: space {start|stop|restart}\n"
        exit 1
        ;;
esac
