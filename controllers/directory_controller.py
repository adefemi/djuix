import os
from .terminal_controller import TerminalController


class DirectoryManager:

    def __init__(self, path):
        self.path = path

    def create_directory(self):
        os.makedirs(self.path, exist_ok=True)

    def create_file(self, path_extension, control="w"):
        file = open(self.path+path_extension, control)
        return file

    @staticmethod
    def format_class_name(name):
        name = name.replace("-", "").split()
        return ''.join([str(n).capitalize() for n in name])

    @staticmethod
    def write_file(file, content):
        file.write(content)
        return file

    @staticmethod
    def close_file(file):
        file.close()
        return file
