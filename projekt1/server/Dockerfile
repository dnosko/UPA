FROM python:3

EXPOSE 5001

WORKDIR /server
COPY . .

RUN pip install -r requirements.txt
CMD [ "python3", "main.py" ]