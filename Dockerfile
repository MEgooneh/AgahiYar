FROM ubuntu:20.04

RUN apt-get update && apt-get install -y python3 python3-pip

RUN pip3 install pytest-playwright pytest-xdist


RUN DEBIAN_FRONTEND=noninteractive apt-get -y install tzdata

RUN playwright install --with-deps chromium 

COPY requirements.txt /

RUN pip3 install -r requirements.txt

WORKDIR /app/

COPY . /app/

ENV TG_KEY="6360256999:AAFVybat-_1m8zDWf_jrWg3giIhPFeH8Hpg"

ENV OPENAI_API_KEY="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"

RUN chmod a+x start.sh

RUN mkdir .auth

CMD ["./start.sh"]


