import os
import re

def replace_words_in_file(file_path, old_word, new_word):
    """Replace words in a file."""
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Perform case-sensitive word replacement
    modified_content = re.sub(r'\b' + re.escape(old_word) + r'\b', new_word, file_content)

    with open(file_path, 'w') as file:
        file.write(modified_content)

def search_and_replace_in_folder(root_folder, old_word, new_word, extensions):
    """Recursively search and replace words in files within a folder."""
    for root, dirs, files in os.walk(root_folder):
        if 'node_modules' in dirs:
            dirs.remove('node_modules')  # Exclude node_modules folder from further traversal
        for file_name in files:
            if any(file_name.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file_name)
                replace_words_in_file(file_path, old_word, new_word)
                print(f"Modified: {file_path}")

# Specify folder path, old word, new word, and file extensions
folder_path = "C:/Users/Lenovo/Desktop/ZenLibrary"
old_word = "sections"
new_word = "sections"
extensions = ['.py', '.html', '.vue', '.css', '.js']  # Add other extensions as needed

# Perform search and replace
search_and_replace_in_folder(folder_path, old_word, new_word, extensions)
