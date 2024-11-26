# Use the official Python image as the base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the Flask app code to the container
COPY . .

# Expose port 5000 to allow access to the app
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "app.py"]
