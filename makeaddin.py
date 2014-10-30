#!/usr/bin/env python
"""makeaddin.py: Create an esriaddin file for this project."""
import os
import re
import sys
import zipfile

VERBOSE_MODE = False
if len(sys.argv) == 2:
    if sys.argv[1] == '--verbose':
        VERBOSE_MODE = True

current_path = os.path.dirname(os.path.abspath(__file__))
out_zip_name = os.path.join(current_path, "..",
                            os.path.basename(current_path) + ".esriaddin")
backup_patterns = {
        'PLUGIN_BACKUP_PATTERN': re.compile(r'.*_addin_[0-9]+[.]py$', re.IGNORECASE),
        'VIM_SWAP_PATTERN': re.compile(r'.*\.sw[op]$', re.IGNORECASE),
        'COMPLIED_PYTHON_PATTERN': re.compile(r'.*\.pyc$', re.IGNORECASE),
        'TODO_PATTERN': re.compile('todo.txt'),
        'OSX_DSTORE': re.compile('.DS_Store')
    }

def looks_like_a_backup(filename):
    """Determine if files are ignorable."""
    is_backup = False
    for pattern in backup_patterns.values():
        if bool(pattern.match(filename)):
            is_backup = True
    return is_backup

# create a new zip file object, set it to be compressed.
with zipfile.ZipFile(out_zip_name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
    # specifically select the top-level files for inclusion
    top_level_files = [
        'config.xml', 'README.md', 'makeaddin.py',
        'LICENSE', 'AUTHORS', 'CHANGELOG'
    ]
    for top_level_file in top_level_files:
        zip_file.write(os.path.join(current_path, top_level_file), top_level_file)
    # add all contents from these directories
    dirs_to_add = ['Images', 'Install']
    for directory in dirs_to_add:
        for (path, dirs, files) in os.walk(os.path.join(current_path, directory)):
            archive_path = os.path.relpath(path, current_path)
            found_file = False
            for fn in (f for f in files if not looks_like_a_backup(f)):
                archive_file = os.path.join(archive_path, fn)
                if VERBOSE_MODE:
                    print archive_file
                zip_file.write(os.path.join(path, fn), archive_file)
                found_file = True
            if not found_file:
                zip_file.writestr(os.path.join(archive_path, 'placeholder.txt'),
                                  "(Empty directory)")
