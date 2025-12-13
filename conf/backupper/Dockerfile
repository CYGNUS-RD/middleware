#FROM alpine:3.20
#RUN apk add --no-cache python3 py3-pip curl bash
#RUN pip3 install --no-cache-dir --break-system-packages -U \
#      mysql-connector-python==8.0.33 \
#      numpy \
#      pandas 
FROM rucio/rucio-clients:latest

WORKDIR /app

# Variabile per il config di rucio
ENV RUCIO_CONFIG=/app/.rucio.cfg

COPY startup.sh /opt/startup.sh
COPY upload_with_weekly_tape_and_disk_lifetime.py /opt/upload_with_weekly_tape_and_disk_lifetime.py

ENTRYPOINT ["/opt/startup.sh"]
