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


## Container vs. Virtual Machine (VM)
- Docker virtualize only the Application layer, i.e. is able to communicates with the host's OS Kernel
    - Size is usually __smaller__ (in MBs)
    - Runs much faster
    - There can be __compatibility__ issue
        - Uses the host's OS kernel
        - For example, an new Linux image cannot communicates with an older version of the Linux kernel on the host machine
        - Containers provide process-level isolation using namespaces and control groups (cgroups). This isolation is generally less robust than VMs but is sufficient for many use cases and offers better performance
    - __Use case__: ideal for microservices architectures, continuous integration/continuous deployment (CI/CD) pipelines, and scenarios where quick scaling and lightweight resource usage are essential
- VM virtualize both the Application and OS Kernel, i.e. VM has its own OS Kernel
    - Each VM includes a full operating system (guest OS) along with the application and its dependencies
    - Size is usually __large__ (in GBs)
    - Runs comparatively slower
    - Install VM on any OS, with __no compatibility__ issue
        - VMs provide strong isolation as each VM is a separate entity with its own OS, kernel, and resources. 
        - This level of isolation can enhance security and stability but comes at a cost of performance overhead
    - __Use case__: suitable for running multiple OS types on the same hardware, providing strong isolation for multi-tenant environments, and running legacy applications that require specific OS versions.

## How to build Docker image

```bash
# Log in to Docker: 
docker login

# Change directory if needed. Make sure requirements.txt is in the same directory
cd Docker

# Build Docker image
docker build -t welcome-app .

# Check if Docker image has been created properly, either from the Docker Desktop app, or using the code below
docker images

# We can now access through our local host http://127.0.0.1:5050, or can do http://localhost:5050/
# This app is now running inside the new Docker container
# Note: http://172.17.0.2:5050 doesn't work, b/c this IP is the IP presented inside the container

# Check new container created
docker ps

# Stop the Docker container (get container ID eacda46c7a43 from the command above)
docker stop eacda46c7a43

```

## Deploy to the Docker Hub Repository
The objective is that now we can download and use it directly

```bash
# Log in Docker Hub https://hub.docker.com/

# Rename to username/app_name (user name has to be in front)
docker tag welcome-app haoyongc/welcome-app

# 'latest' is to indicate which TAG version of the corresponding image to use, as there can be multiple TAGs for one image
docker push haoyongc/welcome-app:latest

# Now go to Docker Hub, you should see the app

# Now we can remove the existing image, then we can download from Docker Repository
docker image rm -f haoyongc/welcome-app

# Now download from Docker Repository
docker pull haoyongc/welcome-app:latest

# Check haoyongc/welcome-app is pulled successfully
docker images

# Now we can run the app
docker run -d -p 5050:5050 haoyongc/welcome-app:latest

# And access from 
http://127.0.0.1:5050 or http://localhost:5050/

```

