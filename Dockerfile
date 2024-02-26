# Use the latest Python Alpine image
FROM python:3.12.2-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY ./requirements.txt /app/requirements.txt

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

#Install Gunicorn
RUN pip install gunicorn

# Copy the application files from your host to your container
COPY ./src /app

# Copy the .env file if you use one for production
COPY ./src/.env /app/.env

# Define the command to run your application
# Note: Adjust the number of workers and threads based on your workload
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "app:app"]

# Expose the port the app runs on
EXPOSE 8000
