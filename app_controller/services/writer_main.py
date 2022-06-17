from controllers.directory_controller import DirectoryManager
from djuix.functions import write_to_file

class WriterMain:
    content_data = ""
    app = None
    
    def __init__(self, app):
        self.app = app
        
    def write_to_file(self, filename, real_file_name=None):
        print(f"writing to {filename} file")
        path_data = f"{self.app.project.project_path}/{self.app.project.name}/{self.app.name}/"
        file_name = f"{filename}s.py"
        if real_file_name:
            file_name = real_file_name
        
        write_to_file(path_data, file_name, self.content_data)
        
    def format_import(self, import_obj):
        for key, value in import_obj.items():
            import_string = ""
            if len(value) < 2:
                import_string = value[0]
            else:
                import_string = ", ".join(i for i in value)
                import_string = f"({import_string})"
            self.content_data += f"from {key} import {import_string}\n"
        
    