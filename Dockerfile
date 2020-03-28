FROM python:3.7
WORKDIR .
ADD app_v1.py .
ADD requirements.txt .
RUN pip install -r requirements.txt
RUN ls -la
EXPOSE 5000
