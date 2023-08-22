# Use the official Selenium image as the base
FROM selenium/standalone-firefox:latest

# Set a working directory
WORKDIR /app

# Install Python and pip (optional, if not already included in the Selenium image)
RUN sudo apt-get update && \
    sudo apt-get install -y python3 python3-pip

# Copy your Selenium Python script to the container
COPY / .


# Install necessary Python packages
RUN pip3 install -r requirements.txt

# Command to run your script
CMD ["python3", "bot.py"]
