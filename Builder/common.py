#
# SDSetup Complex Fetcher
# Copyright (C) 2020 Nichole Mattera
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 
# 02110-1301, USA.
#

import glob
from pathlib import Path
import shutil
import uuid

def generate_temp_path():
    return Path.cwd().joinpath('tmp', str(uuid.uuid4()))

def delete(source):
    sourcePath = Path(source)

    if not sourcePath.exists():
        return

    if sourcePath.is_file():
        sourcePath.unlink()
        return
    
    for fileSourcePath in sourcePath.iterdir():
        delete(fileSourcePath)

        if fileSourcePath.is_dir():
            fileSourcePath.rmdir()

    if sourcePath.is_dir():
        sourcePath.rmdir()
        return

def copy_module_file(module_name, file_name, destination):
    sourcePath = Path.cwd().joinpath('Modules', module_name, file_name)
    return shutil.copyfile(sourcePath, destination)

def copy_module_folder(module_name, folder_name, destination):
    sourcePath = Path.cwd().joinpath('Modules', module_name, file_name)
    return shutil.copytree(sourcePath, destination)

def find_file(pattern):
    return glob.glob(str(pattern), recursive=False)

def mkdir(dest):
    Path(dest).mkdir(parents=True, exist_ok=True)

def move(source, dest):
    sourcePath = Path(source)
    destPath = Path(dest)

    if not sourcePath.exists():
        return

    if sourcePath.is_file():
        sourcePath.rename(destPath)
        return

    if not destPath.exists():
        destPath.mkdir(parents=True, exist_ok=True)
    
    for fileSourcePath in sourcePath.iterdir():
        fileDestPath = destPath.joinpath(fileSourcePath.name)

        if fileSourcePath.is_dir():
            fileDestPath.mkdir(parents=True, exist_ok=True)
        
        move(fileSourcePath, fileDestPath)
