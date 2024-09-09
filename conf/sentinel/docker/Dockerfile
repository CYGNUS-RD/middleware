FROM dodasts/mini-htc:v0

COPY assets/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo

RUN yum-config-manager --save --setopt=htcondor-development.skip_if_unavailable=true

RUN yum -y clean metadata \
    && yum -y install \
              git \
              gcc \
              python36-devel \
              numpy \
    && yum -y clean all 

#
# Install python3 pakage
#
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -U \
    kafka-python \
    mysql-connector \
    numpy \
    pandas \
    boto3 \
    uproot \
    pymongo \
    Cython \
    seaborn \
    scipy \
    git+https://github.com/DODAS-TS/boto3sts \
    git+https://github.com/CYGNUS-RD/cygno.git@v1.0.17 \
    'https://github.com/CYGNUS-RD/middleware/blob/master/midas/midaslib.tar.gz?raw=true'
#
# configure startup script
#
WORKDIR /root/
COPY startup.sh /opt/startup.sh
ENTRYPOINT ["/opt/startup.sh"]
#ENTRYPOINT "/opt/startup.sh && tail -f /var/log/messages"
