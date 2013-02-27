import os
import re
import zipfile

current_path = os.path.dirname(os.path.abspath(__file__))

out_zip_name = os.path.join(current_path, "..",
                            os.path.basename(current_path) + ".esriaddin")

backup_patterns = {
    'PLUGIN_BACKUP_PATTERN': re.compile(".*_addin_[0-9]+[.]py$", re.IGNORECASE),
    'VIM_SWAP_PATTERN': re.compile(".*\.sw[op]$", re.IGNORECASE),
    'COMPLIED_PYTHON_PATTERN': re.compile(".*\.pyc$", re.IGNORECASE),
    'TODO_PATTERN': re.compile('todo.txt')
}

def looks_like_a_backup(filename):
    is_backup = False
    for name, pattern in backup_patterns.items():
        if bool(pattern.match(filename)):
            is_backup = True
    return is_backup

# create a new zip file object, set it to be compressed.
zip_file = zipfile.ZipFile(out_zip_name, 'w', zipfile.ZIP_DEFLATED)
for filename in ('config.xml', 'README.md', 'makeaddin.py'):
    zip_file.write(os.path.join(current_path, filename), filename)
dirs_to_add = ['Images', 'Install']
for directory in dirs_to_add:
    for (path, dirs, files) in os.walk(os.path.join(current_path, directory)):
        archive_path = os.path.relpath(path, current_path)
        found_file = False
        for file in (f for f in files if not looks_like_a_backup(f)):
            archive_file = os.path.join(archive_path, file)
            print archive_file
            zip_file.write(os.path.join(path, file), archive_file)
            found_file = True
        if not found_file:
            zip_file.writestr(os.path.join(archive_path, 'placeholder.txt'), 
                              "(Empty directory)")
zip_file.close()
