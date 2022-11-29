FROM python:3.6.4-slim
COPY ./ /app
WORKDIR /app
RUN pip install -r /app/requirements.txt
COPY ./start.sh /app
ENTRYPOINT ["sh","/app/start.sh"]
