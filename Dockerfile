FROM ubuntu:latest

# Install necessary packages
RUN apt-get update && \
    apt-get install -y python3-pip git

# Install Flask and dependencies
RUN pip3 install flask flask-cors python-ffmpeg

# Clone the repository
RUN git clone https://github.com/accusitive/georgeflipper

# Set the working directory
WORKDIR /georgeflipper

# Expose the port on which the Flask app will run (adjust if needed)
EXPOSE 5000

# Run the Flask app
CMD ["python3", "app.py"]