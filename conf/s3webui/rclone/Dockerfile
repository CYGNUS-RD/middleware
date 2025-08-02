FROM alpine:latest
RUN apk add bash curl grep && rm -rf /var/cache/apk/*
COPY startup.sh /opt/startup.sh
ENTRYPOINT ["/opt/startup.sh"]
