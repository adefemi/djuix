from django.test import TestCase
from app_controller.helpers.model_helper import (
    format_model_name, check_name_change, check_field_names_format,
    check_same_field_names, check_field_change
)

# Create a dummy class for testing


class DummyInstance:
    def __init__(self, field_properties):
        self.field_properties = field_properties


class ModelHelperTestCase(TestCase):

    def test_format_model_name(self):
        self.assertEqual(format_model_name(
            "manufacturer"), "ManufacturerModel")
        self.assertEqual(format_model_name("my model"), "MyModel")
        self.assertEqual(format_model_name("TestModel"), "TestModel")
        self.assertEqual(format_model_name(
            "process Model Obj"), "ProcessModelObjModel")
        self.assertEqual(format_model_name(
            "process-Model_Obj"), "ProcessModelObjModel")

    def test_check_name_change(self):
        # Test case 1: Names are different after formatting
        old_name = "OldModel"
        new_name = "new model"
        # Expected output: True
        self.assertTrue(check_name_change(old_name, new_name))

        # Test case 2: Names are the same after formatting
        old_name = "MyModel"
        new_name = "my model"
        self.assertFalse(check_name_change(old_name, new_name)
                         )  # Expected output: False

        # Test case 3: Names are different but include special characters
        old_name = "SpecialCharModel"
        new_name = "special*char@!$^&Model"
        self.assertFalse(check_name_change(old_name, new_name)
                         )  # Expected output: False

        # Test case 4: Names are the same but have different cases
        old_name = "TestModel"
        new_name = "testmodel"
        self.assertTrue(check_name_change(old_name, new_name)
                        )  # Expected output: True because names are different

        # Test case 5: Names are the same but have different whitespaces and special characters
        old_name = "ProcessModelObjModel"
        new_name = "process-Model_Obj"
        self.assertFalse(check_name_change(old_name, new_name)
                         )  # Expected output: False

    def test_check_field_names_format(self):
        # Test case 1: Valid field names
        valid_data = {
            "field_properties": {
                "fields": [
                    {"name": "field_one"},
                    {"name": "field_two"},
                    {"name": "field_three"}
                ]
            }
        }
        # Expected output: None (no exception)
        self.assertIsNone(check_field_names_format(valid_data))

        # Test case 2: Invalid field names
        invalid_data = {
            "field_properties": {
                "fields": [
                    {"name": "field_one"},
                    # Invalid field name (contains a number)
                    {"name": "field_2"},
                    {"name": "field_three"}
                ]
            }
        }
        with self.assertRaises(Exception) as context:
            check_field_names_format(invalid_data)
        self.assertEqual(str(context.exception),
                         "Invalid name(s): use letters, underscores; no ending _")

    def test_check_same_field_names(self):
        # Test case 1: No duplicate field names
        no_duplicate_data = {
            "field_properties": {
                "fields": [
                    {"name": "field_one"},
                    {"name": "field_two"},
                    {"name": "field_three"}
                ]
            }
        }
        # Expected output: None (no exception)
        self.assertIsNone(check_same_field_names(no_duplicate_data))

        # Test case 2: Duplicate field names
        duplicate_data = {
            "field_properties": {
                "fields": [
                    {"name": "field_one"},
                    {"name": "field_one"},  # Duplicate field name
                    {"name": "field_three"}
                ]
            }
        }
        with self.assertRaises(Exception) as context:
            check_same_field_names(duplicate_data)
        self.assertEqual(str(context.exception),
                         "Model field names cannot be repeated.")

    def test_check_field_change(self):
        # Test case 1: No changes in field properties
        old_instance = DummyInstance({
            "fields": [{"name": "field_one"}, {"name": "field_two"}, {"name": "field_three"}],
            "has_created_at": False,
            "has_updated_at": False
        })

        new_instance = DummyInstance({
            "fields": [{"name": "field_one"}, {"name": "field_two"}, {"name": "field_three"}],
            "has_created_at": False,
            "has_updated_at": False
        })

        # Expected output: False
        self.assertFalse(check_field_change(old_instance, new_instance))

        # Test case 2: Changes in field properties
        old_instance = DummyInstance({
            "fields": [{"name": "field_one"}, {"name": "field_two"}, {"name": "field_three"}],
            "has_created_at": False,
            "has_updated_at": False
        })

        new_instance = DummyInstance({
            "fields": [{"name": "field_one"}, {"name": "field_two_changed"}, {"name": "field_three"}],
            "has_created_at": False,
            "has_updated_at": False
        })

        # Expected output: True
        self.assertTrue(check_field_change(old_instance, new_instance))
