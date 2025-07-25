FROM cern/cc7-base:20220601-1

COPY yum.repos.d /etc/yum.repos.d

ENV OIDC_AGENT=/usr/bin/oidc-agent
#RUN yum install https://dl.fedoraproject.org/pub/archive/epel/7/x86_64/Packages/e/epel-release-7-14.noarch.rpm

RUN yum -y update && yum -y install \
    wget \
    gfal2-util \
    gfal2-all 

WORKDIR /etc/yum.repos.d

#RUN  wget http://repository.egi.eu/sw/production/cas/1/current/repo-files/EGI-trustanchors.repo \
#     &&  wget http://repository.egi.eu/community/software/preview.repository/2.0/releases/repofiles/centos-7-x86_64.repo 

RUN  wget http://repository.egi.eu/sw/production/cas/1/current/repo-files/egi-trustanchors.repo \
     &&  wget http://appdb.egi.eu:9009/api/repofiles/index.php?id=401

RUN yum --setopt=tsflags=nodocs -y install epel-release yum-plugin-ovl \
    && yum --setopt=tsflags=nodocs -y install epel-release yum-plugin-ovl \
    && yum --setopt=tsflags=nodocs -y install fetch-crl wn sysstat \
    && yum clean all \
    && yum install -y ca-policy-egi-core ca-policy-lcg

#RUN  wget https://repo.data.kit.edu/data-kit-edu-centos7.repo

#RUN yum install -y \
#    oidc-agent \
#    && yum clean all 

#RUN sed -i 's/\/bin\/bin\//\/bin\//g' /usr/bin/oidc-agent-service

RUN yum install -y git \
	python3 \
	python-pip

RUN pip3 install --upgrade pip
RUN pip3 install git+https://github.com/DODAS-TS/boto3sts
RUN pip3 install git+https://github.com/CYGNUS-RD/cygno.git
RUN pip3 install mysql-connector
RUN pip2 install numpy==1.16.6

RUN mkdir /root/dev/
WORKDIR /root/dev/
ENTRYPOINT ["/root/dev/init.sh"]
