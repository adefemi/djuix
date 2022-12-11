from controllers.command_template import CommandTemplate
from djuix.functions import send_process_message, write_to_file


class WriteUtils:
    project = None
    content_data = ""
    
    def __init__(self, project):
        self.project = project
        self.write_utils()
        
    def write_utils(self):
        print("Writing project utilities")
        send_process_message(self.project.owner.id, "writing some project utilities...")
        self.content_data += "import re\n"
        self.content_data += "from django.db.models import Q\n"
        
        self.write_get_query()
        self.write_helper()
        
        c = CommandTemplate()
        project_name = self.project.formatted_name
        
        path_data = f"{self.project.project_path}/{project_name}/{project_name}/"
        
        write_to_file(path_data, 'utils.py', self.content_data)
        
    def write_get_query(self):
        self.content_data += "\n\ndef normalize_query(qs, findterms=re.compile(r'" + '"([^"]+)"|(\S+)' + "').findall, normspace=re.compile(r'\s{2,}').sub):\n"
        self.content_data += "\treturn [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(qs)]\n"
        
        self.content_data += "\n\ndef get_query(query_string, search_fields):\n"
        self.content_data += "\tquery = None  # Query to search for every search term\n"
        self.content_data += "\tterms = normalize_query(query_string)\n"
        
        self.content_data += "\n\tfor term in terms:\n"
        self.content_data += "\t\tor_query = None  # Query to search for a given term in each field\n"
        self.content_data += "\t\tfor field_name in search_fields:\n"
        self.content_data += '\t\t\tq = Q(**{"%s__icontains" % field_name: term})\n'
        self.content_data += '\t\t\tif or_query is None:\n'
        self.content_data += '\t\t\t\tor_query = q\n'
        self.content_data += '\t\t\telse:\n'
        self.content_data += '\t\t\t\tor_query = or_query | q\n'
        self.content_data += "\t\tif query is None:\n"
        self.content_data += "\t\t\tquery = or_query\n"
        self.content_data += "\t\telse:\n"
        self.content_data += "\t\t\tquery = query & or_query\n"
        
        self.content_data += "\n\treturn query\n"
    
    def write_helper(self):
        self.content_data += "\n\nclass Helper:\n"
        
        self.content_data += "\t@staticmethod\n"
        self.content_data += "\tdef normalize_request(data):\n"
        
        self.content_data += "\t\ttry:\n"
        self.content_data += "\t\t\tdata._mutable = True\n"
        self.content_data += "\t\t\tresult = data.dict()\n"
        self.content_data += "\t\texcept:\n"
        self.content_data += "\t\t\tresult = data\n"
        
        self.content_data += "\n\t\treturn result\n"