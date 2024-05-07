# Use Debian Bullseye as the base image
FROM python:3.9-slim-bullseye

# Set the working directory inside the container
WORKDIR /loginserver_dockerized

# Update and install required packages
RUN apt-get update && \
    apt-get install -y python3.9 python3-pip

# Install the required Python packages
RUN pip install pymongo
RUN pip install python-dotenv

# Copy the load balancer script into the container
COPY LoginServer/LoginServer.py /loginserver_dockerized

# Command to run the load balancer script
CMD ["python3", "LoginServer.py"]

# Expose UDP and TCP ports
EXPOSE 6969