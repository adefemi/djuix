

from project_controller.sevices import process_app_creation
from project_templates.blog.blog import BlogControl


class CreateBlogTemplate:
    project = None
    app = None
    
    def __init__(self, project):
        self.project = project
        self.create_apps()
        
    def create_apps(self):
        # create user, blog and marketing app
        self.create_blog_app()
        pass
    
    def create_blog_app(self):
        app = process_app_creation({
            "project_id": self.project.id,
            "description": "This is a simple blog app",
            "name": "blog"
        })
        self.app = app
        self.create_blog_artifacts()
    
    
    def create_blog_artifacts(self):
        print("Creating blog artifacts")
        blog_control = BlogControl(self.project, self.app)
        blog_control.createFlow()
        
    def create_user_artifacts(self):
        pass
    
    
        
    