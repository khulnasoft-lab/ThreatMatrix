#!/bin/bash

until cd /opt/deploy/threat_matrix
do
    echo "Waiting for server volume..."
done

if [ "$AWS_SQS" = "True" ]
then
  queues="ingestor.fifo,config.fifo"
else
  queues="ingestor,broadcast,config"
fi

ARGUMENTS="-A threat_matrix.celery worker -n worker_ingestor --uid www-data --gid www-data --time-limit=40000 --pidfile= -Ofair -Q ${queues} -E --autoscale=1,15 --without-gossip"
if [[ $DEBUG == "True" ]] && [[ $DJANGO_TEST_SERVER == "True" ]];
then
    echo "Running celery with autoreload"
    python3 manage.py celery_reload -c "$ARGUMENTS"
else
  /usr/local/bin/celery $ARGUMENTS
fi