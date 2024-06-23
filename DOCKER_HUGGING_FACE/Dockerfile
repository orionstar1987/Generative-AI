## Use the official Python 3.11 image
FROM python:3.11

## Set the working directory to /code
WORKDIR /code

## Copy the current directory contents in the container at /code
COPY ./requirements.txt /code/requirements.txt

## Install the requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

## Set up a new user named "user"
RUN useradd user

## Switch to the "user" user
USER user

