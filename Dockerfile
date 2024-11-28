# Use the official Python 3.11 image as the base image
FROM python:3.11

# Install dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files (if any) to the working directory
COPY . .

# Specify the command to run the application (if applicable)
CMD ["python", "main.py"]

