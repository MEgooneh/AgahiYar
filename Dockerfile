FROM ubuntu:latest


RUN apt-get update && apt-get install -y python3 python3-pip



COPY . /
RUN pip3 install -r requirements.txt

ENV TG_KEY="6360256999:AAFVybat-_1m8zDWf_jrWg3giIhPFeH8Hpg"

CMD ["python3", "bot.py"]
