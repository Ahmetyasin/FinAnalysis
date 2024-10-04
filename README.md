# FinAnalysis API

Welcome to the FinAnalysis API, a powerful tool designed for calculating financial ratios and analyzing financial data. This API allows users to upload Excel files containing financial data, automatically calculates various financial ratios, and provides a scoring system based on the input data. For the time being, the API only accepts Excel files in the same format as data/API_Request_Format.xlsx file.

## Prerequisites

Before you begin, ensure you have Docker installed on your system. Docker is required to build and run the FinAnalysis API container. For Docker installation instructions, please refer to the [official Docker documentation](https://docs.docker.com/get-docker/).

## Installation

To use the FinAnalysis API, you need to clone the repository and build the Docker image.

1. **Clone the Repository**

Start by cloning this repository to your local machine:
```
git clone https://github.com/FinancAI/FinAnalysis.git
```
```
cd FinAnalysis
```
2. **Build the Docker Image**

Build the Docker image using the following command:
```
docker build -t financialanalysis .
```

This command builds a Docker image named `financialanalysis` based on the instructions in the Dockerfile.

## Usage

Once the Docker image is built, you can run the API as a Docker container.

1. **Run the Docker Container**

Use the following command to run the container, mapping port 80 of the container to port 8000 on your host machine:
```
docker run -p 8000:80 financialanalysis
```

2. **Accessing the API**

With the Docker container running, the FinAnalysis API is accessible at `http://localhost:8000`.

You can interact with the API using Swagger UI by navigating to `http://localhost:8000/docs` in your web browser. Swagger UI provides a convenient way to test all the API endpoints directly from your browser without the need for additional tools.

## API Endpoints

The main endpoint for analyzing financial data is:

- **POST /analyze/**: This endpoint accepts an Excel file containing financial data, along with optional parameters for `firm_name` and `sector_name`, and returns calculated financial ratios and scores.



