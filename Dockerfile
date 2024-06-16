# Use Debian Bullseye as the base image
FROM python:3.9-slim-bullseye

# Set the working directory inside the container
WORKDIR /LoginServer_dockerized


# Install the required Python packages
RUN pip install sympy
RUN pip install pymongo

# Copy the load balancer script into the container
COPY LoginServer.py /LoginServer_dockerized
# Command to run the load balancer script
CMD ["python3", "LoginServer.py"]

# Expose UDP and TCP ports
EXPOSE 6969/tcp
EXPOSE 7878/tcp