FROM python:3.8

COPY requirements.txt requirements.txt
COPY videoserver.py videoserver.py
RUN apt-get update && apt-get install -y nano vim
RUN pip install -r requirements.txt

COPY spot_controller.py spot_controller.py
CMD ["/bin/sh"]
