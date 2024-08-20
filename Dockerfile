# Use Debian Bullseye as the base image
FROM python:3.9-slim-bullseye

# Set the working directory inside the container
WORKDIR /server4_dockerized



# Copy the load balancer script into the container
COPY server4.py /server4_dockerized
COPY ChatServer.py /server4_dockerized

# Command to run the load balancer script
CMD ["python3", "server4.py"]

# Expose UDP and TCP ports
EXPOSE 12344/udp
