# Use an official Python runtime as a parent image
FROM python:latest

EXPOSE 80

# Set the working directory in the container
WORKDIR /

# Copy the current directory contents into the container at /app
COPY . /

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Expose the port that Flask is running on

# Run app.py when the container launches
CMD ["python", "api.py"]
