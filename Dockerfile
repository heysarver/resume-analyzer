# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install git
RUN apt-get -y update && \
  apt-get -y install git && \
  rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV ENABLE_DEBUG false
ENV FLASK_APP=app.py

# Expose the application's port
EXPOSE 5000

# Run the application
CMD ["sh", "-c", "flask run --host=0.0.0.0 $(if [ ${ENABLE_DEBUG} = 'true' ]; then echo ''; else echo '--no-debugger'; fi)"]
