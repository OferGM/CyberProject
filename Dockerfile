# Use Debian Bullseye as the base image
FROM python:3.9-slim-bullseye

# Set the working directory inside the container
WORKDIR /gameserver4_dockerized

# Update and install required packages
RUN apt-get update && \
    apt-get install -y python3.9 python3-pip

# Install the required Python packages

# Copy the load balancer script into the container
COPY GameServers/GameServer4.py /gameserver4_dockerized

# Command to run the load balancer script
CMD ["python3", "GameServer4.py"]

# Expose UDP and TCP ports
EXPOSE 12344/udp
