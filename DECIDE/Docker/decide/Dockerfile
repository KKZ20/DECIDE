# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Expose the port that the application listens on.
EXPOSE 5000

# Run your Python script when the container launches
# CMD ["python", "your_script.py"]
CMD ["bash", "-c", "while true; do sleep 1; done"]