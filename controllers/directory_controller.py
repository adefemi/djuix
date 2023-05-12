import os
import shutil

from djuix.helper import Helper


class DirectoryManager:

    def __init__(self, path):
        self.path = path
        print(path)

    @staticmethod
    def create_directory(path):
        os.makedirs(path, exist_ok=True)

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
            return False
        
        return True
    
    @staticmethod
    def copy_directory_contents(src, dst):
        if not os.path.exists(dst):
            os.makedirs(dst)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)