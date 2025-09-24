FROM rucio/rucio-clients:latest

WORKDIR /app

# Installa gfal2, boto3, e strumenti utili
RUN yum update -y && \
    yum install -y epel-release gfal2 python3-pip jq wget ca-certificates && \
    pip3 install boto3 && \
    yum clean all
COPY ./grid-cert /etc/grid-security/certificates

# Variabile per il config di rucio
ENV RUCIO_CONFIG=/app/.rucio.cfg

ENTRYPOINT ["/bin/bash"]
