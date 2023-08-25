FROM ubuntu:20.04

RUN apt-get update && apt-get install -y python3 python3-pip

RUN pip3 install pytest-playwright pytest-xdist

ENV TZ_SELECTION=1

RUN apt install timedatectl

RUN timedatectl set-timezone Asia/Tehran
# Install necessary dependencies
RUN apt-get install -y tzdata

# Set the time zone based on the selected option
RUN ln -fs /usr/share/zoneinfo/Etc/GMT+$TZ_SELECTION /etc/localtime && dpkg-reconfigure --frontend noninteractive tzdata

# Install Playwright with Chromium and its dependencies
RUN echo $TZ_SELECTION | playwright install --with-deps chromium

RUN playwright install --with-deps chromium 

COPY requirements.txt /

RUN pip3 install -r requirements.txt

WORKDIR /app/

COPY . /app/

ENV TG_KEY="6360256999:AAFVybat-_1m8zDWf_jrWg3giIhPFeH8Hpg"

ENV OPENAI_API_KEY="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"

RUN chmod a+x start.sh

CMD ["./start.sh"]


