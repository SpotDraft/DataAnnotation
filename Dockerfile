# Streamlit app deployment dockerfile

from python:3.9-slim

# Set the working directory
WORKDIR  /

# Copy the current directory contents into the container at /app

COPY . /

# Install any needed packages specified in requirements.txt

RUN pip install -r requirements.txt

# Make port 8501 available to the world outside this container

EXPOSE 8501

# Run app.py when the container launches

CMD ["streamlit", "run", "core.py"]

# End of Dockerfile
