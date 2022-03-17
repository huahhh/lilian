FROM python:3.6.8

RUN pip3 install supervisor

RUN rm /etc/apt/sources.list

RUN echo "deb http://mirrors.163.com/debian/ stretch main non-free contrib \
    deb http://mirrors.163.com/debian/ stretch-updates main non-free contrib \
    deb http://mirrors.163.com/debian/ stretch-backports main non-free contrib \
    deb-src http://mirrors.163.com/debian/ stretch main non-free contrib \
    deb-src http://mirrors.163.com/debian/ stretch-updates main non-free contrib \
    deb-src http://mirrors.163.com/debian/ stretch-backports main non-free contrib \
    deb http://mirrors.163.com/debian-security/ stretch/updates main non-free contrib \
    deb-src http://mirrors.163.com/debian-security/ stretch/updates main non-free contrib" >> /etc/apt/sources.list

RUN apt update

RUN apt install -y vim nodejs

RUN mkdir mkdir /var/supervisor && mkdir /home/supervisor

RUN mkdir -p /home/spider/lilian && \
        cd /home/spider/lilian && \
        git init && \
        git remote add origin http://*/lilian.git && \
        git pull origin master && \
        git checkout master

RUN pip3 install -U pip -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com

RUN pip3 install -r /home/spider/lilian/requirements.txt -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com

RUN echo "/home/spider" >> /usr/local/lib/python3.6/site-packages/lilian.pth

COPY start_lilian.sh /home/spider
COPY ./ffmpeg/ffmpeg /bin/ffmpeg
COPY ./ffmpeg/ffprobe /bin/ffprobe

CMD ["/home/spider/start_lilian.sh"]