# Use the specific version of Python as the base image
FROM python:3.10.4-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY src/ src/

# Copy the data directory to the working directory
COPY data/ data/

# Specify the command to run on container start
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
