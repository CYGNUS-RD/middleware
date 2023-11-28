FROM alpine:latest

# Install OpenSSH and create necessary directories
RUN apk update && \
    apk add openssh && \
    mkdir /var/run/sshd

RUN apk add curl \
    bash && rm -rf /var/cache/apk/*

RUN ssh-keygen -A
# Add an SSH user (replace 'username' and 'password' with your desired credentials)
# RUN adduser -D daq
# RUN echo "daq:test" | chpasswd

# Copy SSH configuration file
COPY sshd_config /etc/ssh/sshd_config
# COPY authorized_keys /home/daq/.ssh/authorized_keys

# Expose SSH port
EXPOSE 22

# Start SSH service
# CMD ["/usr/sbin/sshd", "-D"]
COPY startup.sh /opt/startup.sh
ENTRYPOINT ["/opt/startup.sh"]
