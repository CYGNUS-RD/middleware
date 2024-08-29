FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y curl \
	gpg \
	nano \
	git
	
RUN echo 'deb [signed-by=/etc/apt/trusted.gpg.d/kitrepo-archive.gpg] https://repo.data.kit.edu//ubuntu/22.04 ./' >> /etc/apt/sources.list
RUN echo 'deb [signed-by=/etc/apt/trusted.gpg.d/kitrepo-archive.gpg] https://repo.data.kit.edu//ubuntu/jammy ./' >> /etc/apt/sources.list
RUN curl repo.data.kit.edu/repo-data-kit-edu-key.gpg | gpg --dearmor > /etc/apt/trusted.gpg.d/kitrepo-archive.gpg
RUN apt-get update
RUN apt-get install -y oidc-agent

RUN apt-get update \
  && apt-get install -y python3 \
  && apt-get install -y python3-pip \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -U \
    boto3 \
    pandas \
    mysql-connector \
    numpy \
    Pyarrow \
    pymongo \
    git+https://github.com/DODAS-TS/boto3sts \
    git+https://github.com/CYGNUS-RD/cygno.git


#
# configure startup script
#
RUN mkdir /root/dev/
WORKDIR /root/dev/
# ENTRYPOINT ["/root/dev/init.sh"]
