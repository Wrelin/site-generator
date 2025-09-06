import os
import shutil


def clear_directory_contents(directory_path):
    if not os.path.isdir(directory_path):
        print(f"Error: '{directory_path}' is not a valid directory.")
        return

    for item_name in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item_name)
        try:
            if os.path.isfile(item_path):
                os.remove(item_path)  # Remove files
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove subdirectories and their contents
        except Exception as e:
            print(f"Error deleting '{item_path}': {e}")


def get_root_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def clean_docs_and_copy_static():
    root_path = get_root_path()
    docs_path = os.path.join(root_path, 'docs')
    static_path = os.path.join(root_path, 'static')

    clear_directory_contents(docs_path)
    shutil.copytree(static_path, docs_path, dirs_exist_ok=True)


def get_file_content(from_path):
    root_path = get_root_path()
    content_path = os.path.join(root_path, from_path)

    with open(content_path, "r") as file:
        return file.read()

def write_file(dest_path, content):
    root_path = get_root_path()
    file_path = os.path.join(root_path, dest_path)

    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)

    with open(file_path, "w") as file:
        return file.write(content)

def get_markdown_paths(dir_path):
    root_path = get_root_path()
    content_path = os.path.join(root_path, dir_path)

    file_paths = []
    for root, _, files in os.walk(content_path):
        root = root.split(root_path)[1].strip("/")
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
    return file_paths