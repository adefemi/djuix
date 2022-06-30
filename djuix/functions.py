from controllers.directory_controller import DirectoryManager

    
def write_to_file(path_data, file_name, content):
    try:
        directory_manager = DirectoryManager(path_data)
        file_data = directory_manager.create_file(file_name)
        directory_manager.write_file(file_data, content)
        return True
    except Exception as e:
        print(e)
        return False
