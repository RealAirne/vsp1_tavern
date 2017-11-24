FROM ubuntu:latest
RUN apt-get update -y --fix-missing
RUN apt-get install -y python3 python3-pip
RUN pip3 install --upgrade pip

#python3-dev build-essential
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80


ENTRYPOINT ["python3"]
CMD ["-u", "app.py"]