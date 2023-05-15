dockerfile_content = """FROM python:3.9

RUN mkdir /{}

WORKDIR /{}

COPY . /{}/

RUN pip install -r requirements.txt
"""

def get_dockerfile_content(project_identity):
    return dockerfile_content.format(project_identity, project_identity, project_identity)

docker_compose_content = """version: '3'

services:
  web:
    build: .
    command: bash -c "python manage.py runserver 0.0.0.0:{}"
    container_name: {}
    restart: always
    volumes:
      - .:/{}
    ports:
      - "{}:{}"
    networks:
      - {}Net

networks:
  {}Net:
    driver: bridge
"""

def get_docker_compose_content(project_identity, port):
    return docker_compose_content.format(
        port, project_identity, project_identity, port, port, project_identity, project_identity)