FROM alpine:3.20
RUN apk add --no-cache python3 py3-pip curl bash
RUN pip3 install --no-cache-dir --break-system-packages -U \
      mysql-connector-python==8.0.33 \
      numpy \
      pandas \
      boto3==1.35.0 \
      botocore==1.35.99
COPY startup.sh /opt/startup.sh
COPY file2s3_fromHTTPtoken.py /opt/file2s3_fromHTTPtoken.py
WORKDIR /root/
ENTRYPOINT ["/opt/startup.sh"]
