# docker per il DAQ 
# docker build -t gmazzitelli/rucio-uploader:v0.3 .
#
FROM rucio/rucio-clients:latest

WORKDIR /app

# Installa gfal2, boto3, e strumenti utili
RUN yum update -y && \
    yum install -y epel-release gfal2 python3-pip jq wget ca-certificates && \
    pip3 install boto3 && \
    yum clean all
COPY grid-cert /etc/grid-security/certificates

# Copia lo script di upload
COPY rucio_disk_tape_upload.py ./

# Set default config path (può essere sovrascritto con -e RUCIO_CONFIG)
ENV RUCIO_CONFIG=/home/.rucio.cfg

ENTRYPOINT ["python3", "rucio_disk_tape_upload.py"]
