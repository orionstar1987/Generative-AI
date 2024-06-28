## Docker Compose
It's a good practice to have one process/micro-service per container, and use Docker Compose to manage multi-comtainers.
- For example, in a product website, the website can be in one container, and the product service (for product serch) can be in anohter container.
- These containers should be able to talk to each other.

But it's __not very efficient__ to have to configure Docker file, then have to use "docker build", "docker run" for each service one by one.

Docker Compose is a tool for defining and running __multi-container__ Docker applications. With Docker Compose, you can use a single __YAML file (docker-compose.yml)__ to configure and orchestrate your application's services, networks, and volumes, and then use a single command to create and start all the services from your configuration.


## Benefits:
- __Service Definition__: Clearly define all the services your application needs, including their images, ports, volumes, networks, and dependencies
- __Dependency Management__: Use depends_on to specify dependencies between services, ensuring that services start in the correct order.
- __Simplified Commands__: se simple commands (docker-compose up, docker-compose down, etc.) to manage the entire lifecycle of your multi-container application.
- __Environment Management__: Define environment variables and configuration settings for each service in one place.
- __Version Control__: Store your docker-compose.yml file in version control, making it easy to reproduce and share your development environment.

```bash
version: '3.8'

services:
  web:
    image: my-web-app:latest
    ports:
      - "5000:5000"
    depends_on:
      - db

  db:
    image: postgres:latest
    environment:
      POSTGRES_DB: exampledb
      POSTGRES_USER: exampleuser
      POSTGRES_PASSWORD: examplepass
    volumes:
      - db-data:/var/lib/postgresql/data

  redis:
    image: redis:latest

volumes:
  db-data:

```

