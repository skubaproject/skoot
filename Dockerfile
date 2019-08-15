FROM registry.fedoraproject.org/fedora-minimal:30

RUN ln -s /usr/bin/python3 /usr/bin/python && \
    microdnf -y install tar git && \
    cd /opt && \    
    git clone https://github.com/skupperproject/skoot.git
    
WORKDIR /opt/skoot/python/tools

CMD ["bash", "-c", "cat /dev/stdin > /opt/network.conf && source ./export_path.sh && skoot -c /opt/network.conf -o yaml &> /dev/null && tar --create yaml --file /dev/stdout"]
