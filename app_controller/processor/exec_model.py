from app_controller.helpers.model_helper import (
    check_field_addition, check_field_change, check_field_names_format,
    check_slugification, check_same_field_names, )
from app_controller.models import ModelInfo
from app_controller.services.generateModelComponents import GenerateModelComponents
from app_controller.services.write_model import WriteToModel
from app_controller.services.write_serilizer import WriteToSerializer
from app_controller.services.write_url import WriteToUrls
from app_controller.services.write_view import WriteToView


def execute_model_creation(active_model: ModelInfo, has_field_changed=False, is_update=False):
    active_app = active_model.app
    
    WriteToModel(active_app)
    
    if not is_update:
        GenerateModelComponents(active_model)    
    
    WriteToSerializer(active_app)
    WriteToView(active_app)
    WriteToUrls(active_app)

    if has_field_changed:
        active_app.project.run_migration = True
        active_app.project.save()
    
        
def execute_model_update(current_instance: ModelInfo, request_data):
    check_same_field_names(request_data)
    check_field_names_format(request_data)
    check_slugification(request_data)
    check_field_addition(current_instance, request_data)
    has_field_changed = check_field_change(current_instance, request_data)
    
    return has_field_changed