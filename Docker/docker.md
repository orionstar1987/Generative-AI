## Containers

- A way to package application with all the necessary dependencies and configuration
- Portable artifact, easily share and move this package to any environment
- Makes the development and deployment easier and more efficient



## [Docker](https://docs.docker.com/guides/docker-overview/)
- Docker is an open platform for developing, shipping, and running applications. 
- Docker enables you to separate your applications from your infrastructure so you can deliver software quickly.


## Docker Image and Containers
- Docker provides the ability to package and run an application in a loosely isolated environment called a container
- __Docker Image__: a combination of layers of images. For example, python 3.11 installed can be a Image
    - It is a __blueprint__ for containers, i.e. a package of artifacts
    - Each layer represents an instruction in the image’s Dockerfile
    - A Docker image is a read-only template that contains the instructions for creating a Docker container. It includes the application code, libraries, dependencies, tools, and other files that the application needs to run
    - An image is __static__ and does not change
    - Images are identified by their tags (e.g., nginx:latest), which often include a name and a version
- __Docker Container__: when running the Docker Image, it will create a Container
    - A Docker container is a __runtime instance__ of a Docker image, i.e. __Docker Image -> Run__
    - It includes everything the image has, plus a writable layer on top. This allows the container to execute and make changes to its file system
    - A container is dynamic and can be started, stopped, moved, and deleted. It is the running state of an image and can be modified during its runtime
    - Containers are identified by unique IDs (e.g., d4c7e5c4e2a7) and can be named for easier management (e.g., webserver)