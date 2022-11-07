FROM python:3.10.4-slim-buster

RUN adduser --system --group --no-create-home web

WORKDIR /web

#copy the current contents into the containger at /web
COPY . /web

# COPY requirements.txt requirements.txt

#install dependencies
RUN apt-get update  &&\
 apt-get install -y zbar-tools &&\
 apt install -y tesseract-ocr-eng &&\
 apt update &&\
 pip3 install -r requirmentes.txt 

# EXPOSE 5000


RUN chown -R web:web /web
USER web
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "wsgi:app"]
