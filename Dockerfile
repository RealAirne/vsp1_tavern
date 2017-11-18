FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80


ENTRYPOINT ["python"]
CMD ["-u", "app.py"]