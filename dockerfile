FROM python:3.7
ADD . /dlp_code
WORKDIR /dlp_code
EXPOSE 5000
RUN  pip install -r  requirements.txt
CMD gunicorn --bind 0.0.0.0:5000 wsgi:app -t 1500