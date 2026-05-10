# Dockerfile - Instructions to build a Docker image

# Step 1: Start from an official Python image 
FROM python:3.11-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy requirements first 
COPY requirements.txt .

# Step 4: Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of the app code
COPY app.py .

# Step 6: Tell Docker our app listens on port 5000
EXPOSE 5000

# Step 7: Command to run when container starts
CMD ["python", "app.py"]
