# Use Debian Bullseye as the base image
FROM python:3.9-slim-bullseye

# Set the working directory inside the container
WORKDIR /server_dockerized



# Copy the load balancer script into the container
COPY server.py /server_dockerized
COPY ChatServer.py /server_dockerized
# Command to run the load balancer script
CMD ["python3", "server.py"]

# Expose UDP and TCP ports
EXPOSE 12341/udp
EXPOSE 12342/udp
EXPOSE 12343/udp
EXPOSE 12344/udp