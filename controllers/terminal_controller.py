import os
import subprocess
import shlex
from abstractions.defaults import OPTIONAL_PACKAGES, PACKAGE_LIST
from controllers.command_template import CommandTemplate, OsType
from djuix.functions import send_process_message
from .directory_controller import DirectoryManager
import traceback
import re
from datetime import datetime


class TerminalController(CommandTemplate):

    def __init__(self, path, project, delete_if_project_exist=False, active_user_id=None):
        super().__init__(OsType.mac)
        self.path = self.transform_path(path)
        self.project = project
        self.project_name = project.formatted_name
        self.delete_if_project_exist = delete_if_project_exist
        self.active_user = active_user_id

    def get_settings_path(self):
        return f"{self.path}/{self.project_name}/{self.project_name}/"

    def handle_terminal_error(self, error):
        if isinstance(error, str):
            # Extract traceback information from error string
            match = re.search(r'File "(.+)", line (\d+), in (.+)', error)
            if match:
                file_name, line_number, function_name = match.groups()
                line_number = int(line_number)
                error_text = error.splitlines()[-1]
            else:
                raise Exception(error)
        else:
            traceback_list = traceback.extract_tb(error)
            important_trace = traceback_list[-1]
            file_name, line_number, function_name, error_text = important_trace

        raise Exception(error_text)

    def update_pip(self):
        command = "pip install --upgrade pip"
        command_template = self.get_access_template(command)
        p = subprocess.Popen(
            command_template, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            self.handle_terminal_error(err.decode())

        return True

    def create_project(self):
        self.check_user_folder()
        self.check_if_project_already_exist()
        self.create_project_folder()
        self.create_env()
        if self.active_user:
            self.install_packages(new_project=True)

        command = 'django-admin startproject'

        command_template = self.get_access_template(command, self.project_name)
        p = subprocess.Popen(command_template, cwd=self.path,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            self.handle_terminal_error(err.decode())

        self.finalize_process()

        return True

    def check_user_folder(self):
        self.path = os.path.join(
            self.path, self.project.owner.username.lower())
        path_exist = DirectoryManager.check_if_path_exist(self.path)
        if not path_exist:
            DirectoryManager.create_directory(self.path)

    def define_project_standard_name(self):
        return self.project_name + "_main"

    def create_project_folder(self, name=None):
        if self.active_user:
            send_process_message(
                self.active_user, "creating project folder...")
        project_name = self.define_project_standard_name()

        if os.path.exists(self.get_project_full_path()):
            command_template = "rm -r {}"
            command = shlex.split(command_template.format(project_name))
            p = subprocess.Popen(command, cwd=self.path,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
            [_, err] = p.communicate()
            if err:
                self.handle_terminal_error(err.decode())

        p = subprocess.Popen(["mkdir", project_name], cwd=self.path,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            self.handle_terminal_error(err.decode())

        self.path = f"{self.path}/{project_name}"

        print("created project folder")

        return True

    def check_if_project_already_exist(self):
        project_path = os.path.join(
            self.path, self.define_project_standard_name())
        if os.path.exists(project_path):
            if self.delete_if_project_exist:
                DirectoryManager.delete_directory(project_path)
            else:
                raise Exception(
                    "A project with the provided path already exist")
        return True

    def get_env(self):
        return self.project_name + "_env"

    def get_project_full_path(self):
        return f"{self.path}/{self.project_name}"

    @staticmethod
    def transform_path(path):
        return path.replace("\\", "/")

    def create_env(self):
        if self.active_user:
            send_process_message(self.active_user, "creating project env...")
        print(self.path)
        p = subprocess.Popen(["virtualenv", self.get_env()], cwd=self.path,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            self.handle_terminal_error(err.decode())

        print("created virtual env")
        return True

    def install_packages(self, my_packages=PACKAGE_LIST, send_socket=True, new_project=False):
        if send_socket:
            send_process_message(
                self.active_user, "installing required packages...", 0)

        packages_to_use = my_packages
        try:
            if self.project.project_auth:
                packages_to_use.append(OPTIONAL_PACKAGES['pyJwt'])
        except:
            pass

        package_string_list = ""
        for package in packages_to_use:
            package_string_list += package["version"] + " "

        if new_project:
            self.update_pip()

        command = "pip install"
        command_template = self.get_access_template(
            command, package_string_list)
        p = subprocess.Popen(
            command_template, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        [_, err] = p.communicate()
        if err:
            self.handle_terminal_error(err.decode())

        return True

    def create_app(self, app_name):
        command = "python manage.py startapp"
        command_template = self.get_access_template(command, app_name)

        p = subprocess.Popen(command_template, cwd=self.get_project_full_path(),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        p.wait()
        [_, err] = p.communicate()
        if err:
            self.handle_terminal_error(err.decode())
        print("created app")

        # create serializer.py and url.py files
        from .directory_controller import DirectoryManager
        dir_path = f"{self.get_project_full_path()}/{app_name}/"
        dir_manager = DirectoryManager(dir_path)

        dir_manager.create_file("serializers.py", "a")
        dir_manager.create_file("urls.py", "a")
        print("created serializers and urls")

        return True

    def remove_bad_migrations(self, timestamp):
        for app in self.project.project_apps.all():
            try:
                migrations_path = f"{self.get_project_full_path()}/{app.formatted_name}/migrations"
                if os.path.exists(migrations_path):
                    for filename in os.listdir(migrations_path):
                        if filename.endswith('.py') and filename != '__init__.py':
                            # Get the creation time of the migration file
                            migration_file_path = os.path.join(migrations_path, filename)
                            creation_time = datetime.fromtimestamp(os.path.getctime(migration_file_path))

                            # Compare the creation time with the threshold
                            if creation_time > timestamp:
                                # Delete the migration file
                                os.remove(migration_file_path)
                                print(f"Deleted migration file: {migration_file_path}")
            except Exception as e:
                print(f"Error processing app '{app}': {e}")

    def run_migration(self):
        settings_path = f"{self.project_name}.settings"
        export_settings = f"DJANGO_SETTINGS_MODULE={settings_path}"

        export_op_key = "SET"
        if self.os_type == OsType.mac:
            export_op_key = "export"

        project_dir = self.get_project_full_path()

        timestamp_threshold = datetime.now()
        command = f"{export_op_key} {export_settings} && cd {project_dir} && python manage.py makemigrations --noinput && python manage.py migrate"
        command_template = self.get_access_template(command, "")

        p = subprocess.Popen(
            command_template, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        [_, err] = p.communicate()
        if err:
            self.remove_bad_migrations(timestamp_threshold)
            self.handle_terminal_error(err.decode())

        if p.returncode == 3:
            raise Exception(
                "We could not fulfill the request for the modification. We sugestions you provide a default value for fields just added")

        return True

    def finalize_process(self):
        # freeze out the required packages
        django_folder_path = os.path.join(self.path, self.project_name)
        command = "pip freeze > requirements.txt"
        command_template = self.get_access_template(command)
        p = subprocess.Popen(command_template, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, cwd=django_folder_path)
        p.wait()
        [_, err] = p.communicate()
        if err:
            self.handle_terminal_error(err.decode())

        return True
