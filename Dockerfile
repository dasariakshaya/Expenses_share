# Use the official, lightweight Python 3.11 image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first (this caches dependencies to make future builds faster)
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your application code into the container
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# The command to start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]