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

import common
import config
from github import Github
import json
from pathlib import Path
import re
import shutil
import urllib.request
import uuid
import zipfile

gh = Github(config.github_username, config.github_password)

def get_latest_release(module, include_prereleases = True):
    try:
        repo = gh.get_repo(f'{module["git"]["org_name"]}/{module["git"]["repo_name"]}')
    except:
        print(f'[Error] Unable to find repo: {module["git"]["org_name"]}/{module["git"]["repo_name"]}')
        return None
    
    releases = repo.get_releases()
    if releases.totalCount == 0:
        print(f'[Error] Unable to find any releases for repo: {module["git"]["org_name"]}/{module["git"]["repo_name"]}')
        return None

    if include_prereleases:
        return releases[0]

    for release in releases:
        if not release.prerelease:
            return release
    
    return None

def download_asset(module, release, index):
    pattern = module['git']['asset_patterns'][index]

    if release is None:
        return None
    
    matched_asset = None
    for asset in release.get_assets():
        if re.search(pattern, asset.name):
            matched_asset = asset
            break

    if matched_asset is None:
        print(f'[Error] Unable to find asset that match pattern: "{pattern}"')
        return None

    download_path = common.generate_temp_path()
    urllib.request.urlretrieve(matched_asset.browser_download_url, download_path)

    return download_path

def find_asset(release, pattern):
    for asset in release.get_assets():
        if re.search(pattern, asset.name):
            return asset

    return None

def download_atmosphere(module, temp_directory):
    release = get_latest_release(module)
    bundle_path = download_asset(module, release, 0)
    if bundle_path is None:
        return None

    with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
        zip_ref.extractall(temp_directory)
    
    common.delete(bundle_path)
    common.delete(temp_directory.joinpath('switch/reboot_to_payload.nro'))
    common.delete(temp_directory.joinpath('switch'))
    
    payload_path = download_asset(module, release, 1)
    if payload_path is None:
        return None

    common.mkdir(temp_directory.joinpath('../hekate_musthave/bootloader/payloads'))
    shutil.copyfile(payload_path, temp_directory.joinpath('../hekate_musthave/bootloader/payloads/fusee-primary.bin'))

    common.mkdir(temp_directory.joinpath('../atmosphere'))
    common.move(payload_path, temp_directory.joinpath('../atmosphere/fusee-primary.bin'))

    common.copy_module_file('atmosphere', 'system_settings.ini', temp_directory.joinpath('atmosphere/config/system_settings.ini'))

    common.delete(temp_directory.joinpath('hbmenu.nro'))

    return release.tag_name

def download_hekate(module, temp_directory):
    release = get_latest_release(module)
    bundle_path = download_asset(module, release, 0)
    if bundle_path is None:
        return None

    with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
        zip_ref.extractall(temp_directory)

    common.delete(bundle_path)
    
    common.copy_module_file('hekate', 'hekate_ipl.ini', temp_directory.joinpath('bootloader/hekate_ipl.ini'))

    payload = common.find_file(temp_directory.joinpath('hekate_ctcaer_*.bin'))
    if len(payload) != 0:
        shutil.copyfile(payload[0], temp_directory.joinpath('bootloader/update.bin'))
        common.mkdir(temp_directory.joinpath('atmosphere'))
        shutil.copyfile(payload[0], temp_directory.joinpath('atmosphere/reboot_payload.bin'))

        common.mkdir(temp_directory.joinpath('../hekate'))
        common.move(payload[0], temp_directory.joinpath('../hekate/', Path(payload[0]).name))

    common.delete(temp_directory.joinpath('nyx_usb_max_rate (run once per windows pc).reg'))
    
    return release.tag_name

def download_hekate_icons(module, temp_directory):
    release = get_latest_release(module)
    bundle_path = download_asset(module, release, 0)
    if bundle_path is None:
        return None

    with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
        zip_ref.extractall(temp_directory)
    
    common.delete(bundle_path)
    common.copy_module_file('hekate_icons', 'hekate_ipl.ini', temp_directory.joinpath('bootloader/hekate_ipl.ini'))

    return release.tag_name

def download_emuiibo(module, temp_directory):
    release = get_latest_release(module)
    bundle_path = download_asset(module, release, 0)
    if bundle_path is None:
        return None
    
    with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
        zip_ref.extractall(temp_directory)

    common.delete(bundle_path)
    common.mkdir(temp_directory.joinpath('atmosphere/contents'))
    common.move(temp_directory.joinpath('SdOut/atmosphere/contents/0100000000000352'), temp_directory.joinpath('atmosphere/contents/0100000000000352'))
    common.mkdir(temp_directory.joinpath('switch/.overlays'))
    common.move(temp_directory.joinpath('SdOut/switch/.overlays/emuiibo.ovl'), temp_directory.joinpath('switch/.overlays/emuiibo.ovl'))  
    common.delete(temp_directory.joinpath('SdOut'))
    common.copy_module_file('emuiibo', 'toolbox.json', temp_directory.joinpath('atmosphere/contents/0100000000000352/toolbox.json'))

    return release.tag_name

def download_ldn_mitm(module, temp_directory):
    release = get_latest_release(module)
    bundle_path = download_asset(module, release, 0)
    if bundle_path is None:
        return None
    
    with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
        zip_ref.extractall(temp_directory)
    
    common.delete(bundle_path)
    common.copy_module_file('ldn_mitm', 'toolbox.json', temp_directory.joinpath('atmosphere/contents/4200000000000010/toolbox.json'))

    return release.tag_name

def download_lockpick_rcm(module, temp_directory):
    release = get_latest_release(module)
    payload_path = download_asset(module, release, 0)
    if payload_path is None:
        return None

    common.move(payload_path, temp_directory.joinpath('Lockpick_RCM.bin'))

    return release.tag_name

def download_nx_ovlloader(module, temp_directory):
    release = get_latest_release(module)
    bundle_path = download_asset(module, release, 0)
    if bundle_path is None:
        return None
    
    with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
        zip_ref.extractall(temp_directory)
    
    common.delete(bundle_path)

    return release.tag_name

def download_ovl_sysmodules(module, temp_directory):
    release = get_latest_release(module)
    app_path = download_asset(module, release, 0)
    if app_path is None:
        return None

    common.mkdir(temp_directory.joinpath('switch/.overlays'))
    common.move(app_path, temp_directory.joinpath('switch/.overlays/ovlSysmodules.ovl'))

    return release.tag_name

def download_status_monitor_overlay(module, temp_directory):
    release = get_latest_release(module)
    app_path = download_asset(module, release, 0)
    if app_path is None:
        return None

    common.mkdir(temp_directory.joinpath('switch/.overlays'))
    common.move(app_path, temp_directory.joinpath('switch/.overlays/Status-Monitor-Overlay.ovl'))

    return release.tag_name

def download_sys_clk(module, temp_directory):
    release = get_latest_release(module)
    bundle_path = download_asset(module, release, 0)
    if bundle_path is None:
        return None
    
    with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
        zip_ref.extractall(temp_directory)

    common.delete(bundle_path)
    common.delete(temp_directory.joinpath('README.md'))
    common.copy_module_file('sys-clk', 'toolbox.json', temp_directory.joinpath('atmosphere/contents/00FF0000636C6BFF/toolbox.json'))

    return release.tag_name

def download_sys_con(module, temp_directory):
    release = get_latest_release(module)
    bundle_path = download_asset(module, release, 0)
    if bundle_path is None:
        return None
    
    with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
        zip_ref.extractall(temp_directory)

    common.delete(bundle_path)

    return release.tag_name

def download_sys_ftpd_light(module, temp_directory):
    release = get_latest_release(module)
    bundle_path = download_asset(module, release, 0)
    if bundle_path is None:
        return None
    
    with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
        zip_ref.extractall(temp_directory)

    common.delete(bundle_path)

    return release.tag_name

def download_tesla_menu(module, temp_directory):
    release = get_latest_release(module)
    bundle_path = download_asset(module, release, 0)
    if bundle_path is None:
        return None
    
    with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
        zip_ref.extractall(temp_directory)
    
    common.delete(bundle_path)

    return release.tag_name

def build(temp_directory, auto_build):
    results = []

    # Open up modules.json
    with open('sdsetup.json') as json_file:
        # Parse JSON
        data = json.load(json_file)

        # Loop through modules
        for module in data:
            # Only show prompts when it's not an auto build.
            if not auto_build:
                print(f'Downloading {module["name"]}...')

            # Make sure module directory is created.
            module_directory = temp_directory.joinpath(module['sdsetup_module_name'])
            common.mkdir(module_directory)

            # Download the module.
            download = globals()[module['download_function_name']]
            version = download(module, module_directory)
            if version is None:
                return None

            # Auto builds have a different prompt at the end for parsing.
            if auto_build:
                results.append(f'{module["sdsetup_module_name"]}:{version}')
            else:
                results.append(f'  {module["name"]} - {version}')

    return results
