FROM alpine:latest
RUN apk --update add --no-cache openssh
RUN apk add curl \
	bash && rm -rf /var/cache/apk/*
COPY startup.sh /opt/startup.sh
ENTRYPOINT ["/opt/startup.sh"]
