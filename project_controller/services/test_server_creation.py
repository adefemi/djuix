from controllers.directory_controller import DirectoryManager
from controllers.terminal_controller import TerminalController
import shutil

from abstractions.defaults import DEFAULT_DEPLOY_DIR
from abstractions.deployment import get_docker_compose_content, get_dockerfile_content
import os

class TestServerCreation:
    def __init__(self, project, port):
        self.project = project
        self.port = port
        
        self.username = project.owner.username
        self.project_deployment_path = os.path.join(DEFAULT_DEPLOY_DIR, self.username)
        
        if not DirectoryManager.check_if_path_exist(self.project_deployment_path):
            DirectoryManager.create_directory(self.project_deployment_path)
            
        self.copy_project_to_deploy()
        self.push_docker_artifacts()
        
        
    def copy_project_to_deploy(self):
        # copy project folder excluding the env file to the deploy folder
        project_path = os.path.join(self.project.project_path, self.project.name)
        shutil.copytree(project_path, self.project_deployment_path)
        self.project_path = os.path.join(self.project_deployment_path, self.project.name)
        
        
    def push_docker_artifacts(self):
        # push the dockerfile and the docker-compose artifact to the project folder
        project_identity = "{}_{}".format(self.project.name, self.username)
        
        dir_controller = DirectoryManager(self.project_path)
        dockerfile = dir_controller.create_file('/Dockerfile')
        dir_controller.write_file(dockerfile, get_dockerfile_content(project_identity))
        
        docker_compose_file = dir_controller.create_file('/docker-compose.yml')
        dir_controller.write_file(docker_compose_file, get_docker_compose_content(project_identity, self.port))