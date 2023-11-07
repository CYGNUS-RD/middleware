FROM alpine:latest
RUN apk --update add python3
RUN apk add curl \
	bash && rm -rf /var/cache/apk/*
COPY startup.sh /opt/startup.sh
ENTRYPOINT ["/opt/startup.sh"]
