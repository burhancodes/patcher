import subprocess
import sys
import os
import shutil
import argparse
import requests
from colorama import Fore, Style, init

# Constants
APKTOOL_URL = "https://github.com/iBotPeaches/Apktool/releases/download/v2.10.0/apktool_2.10.0.jar"
APKTOOL_JAR = "apktool.jar"
TG_PATCHER_URL = "https://raw.githubusercontent.com/AbhiTheModder/termux-scripts/main/tgpatcher.py"
TG_PATCHER_SCRIPT = "tgpatcher.py"

# Patch sets
PATCH_SETS = {
    "pad": "1,2,3,4,6,7,8,9,10,11,12,13,14,15,16,17"
}

init(autoreset=True)

def download_file(url, filename):
    print(Fore.CYAN + f"Downloading {filename} from {url}...")
    response = requests.get(url, stream=True)
    with open(filename, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print(Fore.GREEN + f"{filename} downloaded successfully.")

def download_apktool():
    if not os.path.exists(APKTOOL_JAR):
        download_file(APKTOOL_URL, APKTOOL_JAR)
    else:
        print(Fore.GREEN + f"{APKTOOL_JAR} already exists.")

def download_tgpatcher():
    download_file(TG_PATCHER_URL, TG_PATCHER_SCRIPT)

def find_apk_file():
    apk_files = [file for file in os.listdir() if file.endswith(".apk")]
    if not apk_files:
        print(Fore.RED + "No APK files found in the current directory. Please add an APK and try again.")
        exit(1)
    if len(apk_files) > 1:
        print(Fore.YELLOW + "Multiple APK files found:")
        for idx, apk in enumerate(apk_files, start=1):
            print(Fore.YELLOW + f"{idx}. {apk}")
        choice = int(input(Fore.GREEN + "Enter the number of the APK you want to process: "))
        return apk_files[choice - 1]
    return apk_files[0]

def decompile_apk(apk_file):
    print(Fore.CYAN + f"Decompiling the APK: {apk_file}...")
    decompile_dir = apk_file.replace(".apk", "_decompiled")
    subprocess.run(["java", "-jar", APKTOOL_JAR, "d", apk_file, "-o", decompile_dir, "--force", "--no-res"])
    print(Fore.GREEN + f"APK decompiled to: {decompile_dir}")
    return os.path.abspath(decompile_dir)

def execute_tgpatcher(decompile_dir, patches):
    print(Fore.CYAN + f"Running tgpatcher script with patches: {patches}...")
    subprocess.run(
        ["python3", TG_PATCHER_SCRIPT],
        input=f"{decompile_dir}\n{patches}\n",
        text=True
    )
    print(Fore.GREEN + "tgpatcher script completed.")

def recompile_apk(decompile_dir):
    print(Fore.CYAN + "Recompiling the APK...")
    recompiled_apk = decompile_dir.replace("_decompiled", "_patched.apk")
    subprocess.run(["java", "-jar", APKTOOL_JAR, "b", decompile_dir, "-o", recompiled_apk, "--no-res"])
    print(Fore.GREEN + f"Recompiled APK: {recompiled_apk}")
    
    print(Fore.CYAN + f"Cleaning up: Removing decompiled directory {decompile_dir}...")
    shutil.rmtree(decompile_dir)
    print(Fore.GREEN + "Decompiled directory removed.")    

def main():
    parser = argparse.ArgumentParser(description="Telegram Patcher")
    parser.add_argument("mode", type=str, choices=PATCH_SETS.keys(), help="Select the patch set to apply: pad")
    args = parser.parse_args()
    
    patches = PATCH_SETS[args.mode]
    
    download_apktool()
    download_tgpatcher()
    apk_file = find_apk_file()
    decompiled_dir = decompile_apk(apk_file)
    execute_tgpatcher(decompiled_dir, patches)
    recompile_apk(decompiled_dir)

if __name__ == "__main__":
    main()
