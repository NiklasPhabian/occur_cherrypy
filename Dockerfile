# Use an official Python runtime as a base image
FROM python:3.5-slim

# Copy the requirements.txt into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD occur /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run the main when the container launches
CMD ["python", "main.py"]

