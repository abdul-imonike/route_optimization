# Use an official Python runtime as an image
FROM python:2.7.9

# The EXPOSE instruction indicates the ports on which a container 
# will listen for connections
# Since Flask apps listen to port 5000  by default, we expose it
EXPOSE 5000

# Sets the working directory for following COPY and CMD instructions
# Notice we haven’t created a directory by this name - this instruction 
# creates a directory with this name if it doesn’t exist
WORKDIR /control_search

# Install any needed packages specified in requirements.txt
COPY requirements.txt /control_search
RUN pip install -r requirements.txt

# COPY ./db /docker-entrypoint-initdb.d/ 

# Run app.py when the container launches
COPY . /control_search
CMD python control_search.py
