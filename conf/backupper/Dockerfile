FROM alpine:latest
RUN apk --update add python3
RUN apk add curl \
	bash && rm -rf /var/cache/apk/*
RUN apk add py3-pip
RUN pip3 install --no-cache-dir -U \
    mysql-connector==2.2.9 \
    numpy \
    pandas \
    boto3 

COPY startup.sh /opt/startup.sh
COPY file2s3_fromHTTPtoken.py /opt/file2s3_fromHTTPtoken.py
WORKDIR /root/
ENTRYPOINT ["/opt/startup.sh"]
