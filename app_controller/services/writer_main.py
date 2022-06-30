from controllers.command_template import CommandTemplate
from djuix.functions import write_to_file

class WriterMain(CommandTemplate):
    content_data = ""
    app = None
    
    def __init__(self, app):
        self.app = app
        
    def write_to_file(self, filename, real_file_name=None):
        print(f"writing to {filename} file")
        p_name = self.get_formatted_name(self.app.project.name)
        a_name = self.get_formatted_name(self.app.name)
        path_data = f"{self.app.project.project_path}/{p_name}/{a_name}/"
        file_name = f"{filename}s.py"
        if real_file_name:
            file_name = real_file_name
        
        write_to_file(path_data, file_name, self.content_data)
        
    def format_import(self, import_obj):
        for key, value in import_obj.items():
            if key == "generic":
                for i in value:
                    self.content_data += f"import {i}"
            
            else:
                import_string = ""
                if len(value) < 2:
                    import_string = value[0]
                else:
                    import_string = ", ".join(i for i in value)
                    import_string = f"({import_string})"
                self.content_data += f"from {key} import {import_string}\n"
        
    