FROM python:3.7

MAINTAINER Aleksei Nagaev "ak.nagaev@gmail.com"

COPY ./requirements.txt /requirements.txt

WORKDIR /

RUN pip install -r requirements.txt

COPY . /

ENTRYPOINT [ "python3" ]

CMD [ "app/app.py" ]