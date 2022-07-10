import shlex


class OsType:
    windows = 'windows'
    linux = 'linux'
    mac = 'mac'

class CommandTemplate:
    os_type:OsType = OsType.windows
    
    def __init__(self, os_type: OsType = OsType.linux):
        self.os_type = os_type
        
    def get_formatted_name(self, name):
        return name.lower().replace(" ", "_")
    
    def get_formatted_class_name(self, name):
        return name.capitalize().replace(" ", "")
    
    def get_env_full_path(self):
        return f"{self.path}/{self.get_env()}{self.get_env_path()}"
    
    def get_env_path(self):
        if self.os_type == OsType.windows:
            return "/Scripts/activate.bat"
        return "/bin/activate"
        
    def get_access_template(self, command, *args):
        if self.os_type == OsType.windows:
            result = f"{self.get_env_full_path()} && {command} {args}"
        else:
            command_template = '/bin/bash -c "source {} && {} {}"'
            my_args = [""]
            if args:
                my_args = args
            result = shlex.split(command_template.format(self.get_env_full_path(), command, *my_args))
            
        return result
    
    def get_python_command(self):
        if self.os_type == OsType.windows:
            return "python.exe"
        return "python"