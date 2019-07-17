# network-creator

This is an attempt to create a public private router network over Kubernetes

This project is not very sophisticated (yet)

1. cd python/tools
2. source export_path.sh
3. skoot -c full-path-of-network-config -o full-path-of-output-yaml (example network config can be found in the network-configs folder). This will create router 
   configs in the generated-configs folder. Also creates certificate authority and related certificates in the generated-certs folder 
4. The skoot tool (for now) can only be executed from the python/tools folder




