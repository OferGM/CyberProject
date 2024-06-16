# Use Debian Bullseye as the base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /loginserver_dockerized

# Copy the load balancer script into the container
COPY LoginServer.py /loginserver_dockerized

RUN pip install pymongo
RUN pip install sympy

# Command to run the load balancer script
CMD ["python3", "LoginServer.py"]

# Expose UDP and TCP ports
EXPOSE 8888/tcp
EXPOSE 7878/tcp