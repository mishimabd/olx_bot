# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container
COPY . .

# Expose the Flask port
EXPOSE 80

# Expose the Telegram port if necessary (this might be optional depending on your bot's configuration)
EXPOSE 8443

# Run main.py when the container launches
CMD ["python", "main.py"]
