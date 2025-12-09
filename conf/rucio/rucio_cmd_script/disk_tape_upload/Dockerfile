# docker per il DAQ 
# docker build -t gmazzitelli/rucio-uploader:v0.1 .
#
FROM rucio/rucio-clients:latest

WORKDIR /app

# Copia lo script di upload
COPY rucio_disk_tape_upload.py ./

# Set default config path (può essere sovrascritto con -e RUCIO_CONFIG)
ENV RUCIO_CONFIG=/home/.rucio.cfg

ENTRYPOINT ["python3", "rucio_disk_tape_upload.py"]
