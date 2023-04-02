import re
from abstractions.enums import ModelFieldTypes

from app_controller.models import ViewsInfo


def format_model_name(name):
    # Replace special characters in the input string with a whitespace
    name = re.sub(r'[^a-zA-Z0-9\s]', ' ', name)

    # Split the input string into words
    words = name.split()

    # Capitalize the first letter of each word except the last one if it contains "Model"
    capitalized_words = []
    for i, word in enumerate(words):
        if i == len(words) - 1 and "Model" in word:
            capitalized_words.append(word)
        else:
            capitalized_words.append(word.capitalize())

    # Check if the last word contains "Model", if not, append "Model" to the end
    if "Model" not in capitalized_words[-1]:
        capitalized_words.append("Model")

    # Join the capitalized words
    formatted_name = "".join(capitalized_words)

    return formatted_name


def check_name_change(old_name, new_name):
    new_name = format_model_name(new_name)
    if old_name == new_name:
        return False
    return True


def check_field_change(old_instance, new_instance):
    old_instance_fields = {
        "fields": old_instance.field_properties["fields"],
        "has_created_at": old_instance.field_properties.get("has_created_at", False),
        "has_updated_at": old_instance.field_properties.get("has_updated_at", False),
    }

    new_instance_fields = {
        "fields": new_instance["field_properties"]["fields"],
        "has_created_at": new_instance["field_properties"].get("has_created_at", False),
        "has_updated_at": new_instance["field_properties"].get("has_updated_at", False),
    }

    if str(old_instance_fields) == str(new_instance_fields):
        return False

    return True


def check_same_field_names(new_data):
    new_fields = new_data["field_properties"]["fields"]

    existing_field_names = []
    for field in new_fields:
        if field["name"] in existing_field_names:
            raise Exception("Model field names cannot be repeated.")

        existing_field_names.append(field["name"])


def check_field_names_format(new_data):
    new_fields = new_data["field_properties"]["fields"]
    pattern = re.compile(r'^[a-zA-Z]+(_?[a-zA-Z]+)*$')
    for field in new_fields:
        if not pattern.match(field["name"]):
            raise Exception(
                "Invalid name(s): use letters, underscores; no ending _")


def check_slugification(new_data):
    new_fields = new_data["field_properties"]["fields"]
    # check if there is a slug field in the fields
    slug_fields = []
    field_names = []
    for field in new_fields:
        if field["field_type"] == ModelFieldTypes.SlugField:
            slug_fields.append(field)
        else:
            field_names.append(field["name"])

    for slug_field in slug_fields:
        ref = slug_field["field_properties"]["field_reference"]
        if not ref in field_names:
            raise Exception(
                "One or more slug field reference cannot be found.")


def check_field_addition(model_instance, request_data):
    has_migration = model_instance.has_created_migration
    if not has_migration:
        return

    current_fields = model_instance.field_properties["fields"]
    new_fields = request_data["field_properties"]["fields"]

    if len(new_fields) > len(current_fields):
        # A new field was added, find the new field
        # Store the names of existing fields in a list
        existing_field_names = [field["name"] for field in current_fields]

        # Check which of the fields from the new_fields is not in the existing_field_names
        new_field_content = [
            field for field in new_fields if field["name"] not in existing_field_names]

        # Check if the new field is null or has a default value, if not then raise an exception that this will affect the migrations
        for field in new_field_content:
            field_props = field["field_properties"]
            if not field_props.get("default", None) and not field_props.get("null", None):
                raise Exception(
                    "New fields in a migrated model must have a default value or be nullable.")


def check_implement_search_fields(
        existing_fields, model_instance, modify_fields, new_model_name):
    # Get all ViewsInfo objects related to the app_id of the model_instance
    app_views = ViewsInfo.objects.filter(app_id=model_instance.app.id)

    # Create a set to store the modified field search strings
    modified_search_fields = set()

    # Iterate through existing_fields dictionary
    for field_name, field_type in existing_fields.items():
        if field_name in modify_fields:
            # Add both the field_name and the combination of formatted_model_name and field_name to the set
            modified_search_fields.add(field_name)
            modified_search_fields.add(f'{model_instance.name}.{field_name}')

    for view in app_views:
        # Check if the view has implement_search in its field_properties
        implement_search = view.field_properties.get('implement_search', None)
        if implement_search:
            search_fields = implement_search["search_fields"]

            # Check if there is an intersection between modified_search_fields and search_fields
            if modified_search_fields.intersection(search_fields):
                field_name = modified_search_fields.intersection(
                    search_fields).pop()
                modified_field = modify_fields.get(field_name, None)
                if not modified_field:
                    raise Exception(
                        f"A modified field named was used in {view.name} implement search fields")
                else:
                    # Check if the new field type is a related field
                    new_field_type = modify_fields[field_name]["field_type"]
                    related_field_types = [
                        ModelFieldTypes.ForeignKey,
                        ModelFieldTypes.ManyToManyField,
                        ModelFieldTypes.OneToOneField
                    ]
                    if new_field_type in related_field_types:
                        raise Exception(
                            f"Changing field type to a related field will affect {view.name} implement search fields")
