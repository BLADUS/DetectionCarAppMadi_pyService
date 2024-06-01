def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File '{file_path}' has been successfully deleted.")
        return True
    except Exception as e:
        print(f"Error occurred while deleting file '{file_path}': {e}")
        return False