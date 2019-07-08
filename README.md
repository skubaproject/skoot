# network-creator

This is an attempt to create a public private router network over Kubernetes

This project is not very sophisticated (yet)

1. Login as root user (minor inconvenience for now).
2. cd python/tools
3. source export_path.sh
4. skoot -c full-path-of-network-config (example network config can be found in the network-configs folder). This will create router 
   configs in the generated-configs folder. Also creates certificate authority and related certificates in the generated-certs folder 
5. The skoot tool (for now) can only be executed from the python/tools folder
6. The resulting yaml files can be found in the /etc/qpid-dispatch/yaml folder





