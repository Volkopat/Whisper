# Use an official Python runtime as a parent image
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04 

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for PyTorch, Whisper, FFmpeg, and general build processes
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip \
    cargo \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Copy only the requirements.txt first to leverage Docker cache
COPY requirements.txt /app/

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code
COPY . /app

# Expose the port the app runs on
EXPOSE 7861

# Run the Gradio app when the container launches
CMD ["python3", "run.py"]
