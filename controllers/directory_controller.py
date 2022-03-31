import os
import shutil

from djuix.helper import Helper


class DirectoryManager:

    def __init__(self, path):
        self.path = path

    def create_directory(self):
        os.makedirs(self.path, exist_ok=True)

    def create_file(self, path_extension, control="w"):
        new_path = self.path+path_extension
        try:
            if self.check_if_path_exist(new_path):
                self.delete_file(new_path)
            file = open(new_path, control)
            return file
        except OSError as e:
            Helper.handleException(e)

    @staticmethod
    def format_class_name(name):
        name = name.replace("-", "").split()
        return ''.join([str(n).capitalize() for n in name])

    @staticmethod
    def write_file(file, content):
        try:
            file.write(content)
            return file
        except OSError as e:
            Helper.handleException(e)

    @staticmethod
    def close_file(file):
        file.close()
        return file
    
    @staticmethod
    def delete_file(path):
        try:
            os.remove(path)
        except OSError as e:
            raise Exception(e)

    @staticmethod
    def delete_directory(path):
        try:
            shutil.rmtree(path)
        except OSError as e:
            raise Exception(e)
        
    @staticmethod
    def check_if_path_exist(path):
        if not os.path.exists(path):
            raise Exception("path do not exist")
        
        print("path exist")
        return True