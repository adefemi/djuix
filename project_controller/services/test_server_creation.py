from controllers.directory_controller import DirectoryManager
import shutil
import subprocess
from sentry_sdk import capture_message

from abstractions.defaults import DEFAULT_DEPLOY_DIR
from abstractions.deployment import get_docker_compose_content, get_dockerfile_content
import os

class TestServerCreation:
    def __init__(self, project, port):
        self.project = project
        self.port = port
        
        self.username = project.owner.username
        self.project_deployment_path = os.path.join(DEFAULT_DEPLOY_DIR, self.username)
        self.project_path = os.path.join(self.project_deployment_path, self.project.formatted_name)
        self.project_absolute_path = "/root/djux.io/djuix_deploys/{}/{}".format(
            self.username,
            self.project.formatted_name
        )
        self.project_name = self.project.formatted_name
        self.project_identity = "{}_{}".format(self.project.formatted_name, self.username).replace("_", "-")
        
    def deploy(self):
        if not DirectoryManager.check_if_path_exist(self.project_deployment_path):
            DirectoryManager.create_directory(self.project_deployment_path)
        self.copy_project_to_deploy()
        self.push_docker_artifacts()
        return self.deploy_up()
        
    def destroy(self):
        self.deploy_down()
        
        
    def copy_project_to_deploy(self):
        # copy project folder excluding the env file to the deploy folder
        project_path = os.path.join(self.project.project_path, self.project.formatted_name)
        shutil.copytree(project_path, self.project_path)
        
    def push_docker_artifacts(self):
        # push the dockerfile and the docker-compose artifact to the project folder
        dir_controller = DirectoryManager(self.project_path)
        dockerfile = dir_controller.create_file('/Dockerfile')
        dir_controller.write_file(dockerfile, get_dockerfile_content(self.project_identity))
        
        docker_compose_file = dir_controller.create_file('/docker-compose.yml')
        dir_controller.write_file(docker_compose_file, get_docker_compose_content(self.project_identity, self.port))
        
    def exec_script(self, script):
        command = [
            "ssh",
            "-oStrictHostKeyChecking=no", 
            "-i", 
            "/root/.ssh/id_rsa", 
            "root@188.166.149.188", 
            "./djux.io/djuix_deploys/{} {} {} {} {}".format(
                script,
                self.port,
                self.project_identity,
                self.project_absolute_path,
                self.project_name
            )
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        print("Output: ", result.stdout)
        print("Errors: ", result.stderr)
        
    def deploy_up(self):
        script_path = "deploy_up.sh"
        
        self.exec_script(script_path)
        
        return f"{self.project_identity}.api.djuix.io"
    
    def deploy_down(self):
        script_path = "deploy_down.sh"
        
        self.exec_script(script_path)
        

def close_test_server(test_server):
    test_server_creation = TestServerCreation(test_server.project, test_server.port)
    
    try:
        test_server_creation.deploy_down()
        test_server.delete()
    except Exception as e:
        capture_message(e)
    
    