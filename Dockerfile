FROM python:3.7
WORKDIR .
ADD requirements.txt .
RUN pip install -r requirements.txt
RUN ls -la
EXPOSE 5000
EXPOSE 5001
