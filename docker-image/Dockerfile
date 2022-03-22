# build a new image based on centos:centos7 image
FROM centos:centos7
# open port 22 for ssh application, port 8888 for jupyter and 9905 for http api
EXPOSE 22 8888 9905
# set work directory
WORKDIR /home/aghs
# copy files
COPY ./* /home/aghs
RUN yum -y update \
    # install necessary softwares
    && yum install git vim wget openssh-server -y \
    # modify /etc/ssh/sshd_config
    && sed -i 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config \
    # generate ssh key
    && ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key \
    && ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key \
    # set the password of root, and the default password is "yuansong"
    && echo "root:yuansong"|chpasswd \ 
