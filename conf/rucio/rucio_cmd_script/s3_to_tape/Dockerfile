FROM rucio/rucio-clients:latest

WORKDIR /app

# Installa gfal2 e boto3 usando yum e pip3

RUN yum update -y && \
    yum install -y epel-release gfal2 python3-pip && \
    pip3 install boto3 && \
    yum clean all

RUN yum install -y ca-certificates && update-ca-trust

# Variabile per il config di rucio
ENV RUCIO_CONFIG=/app/.rucio.cfg


# Copy script into container
COPY register_s3_path_to_tape.py  .

# Entry point (default can be overridden)
ENTRYPOINT ["python3", "register_s3_path_to_tape.py"]
