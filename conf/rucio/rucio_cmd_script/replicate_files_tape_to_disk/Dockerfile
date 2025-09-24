FROM rucio/rucio-clients:latest

WORKDIR /app

# Copia lo script di replica
COPY replicate_files_tape_to_disk.py ./

# Set il file di config di default (può essere sovrascritto con -e RUCIO_CONFIG)
ENV RUCIO_CONFIG=/home/.rucio.cfg

ENTRYPOINT ["python3", "replicate_files_tape_to_disk.py"]
