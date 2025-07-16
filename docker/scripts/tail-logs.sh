#!/bin/bash  

docker exec threatmatrix_uwsgi ls -al /var/log/threat_matrix/"$1" 
docker exec -ti threatmatrix_uwsgi tail -f /var/log/threat_matrix/"$1"  
