### Helm chart for Open Streaming Platform

https://hub.docker.com/r/deamos/openstreamingplatform

# First run redis

helm install --name redis-cluster stable/redis

# Install a DB such as MySQL

helm install --name my-release stable/mysql

# Run OSP

helm install --name osp -f values.yaml .