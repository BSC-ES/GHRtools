import subprocess
from pathlib import Path
import shutil

import argparse
import os
import requests

PKG_MAP = {
    "data4health": {
        "cran_url": "https://cran.r-project.org/web/packages/data4health/index.html",
        "extracted_pkg_path": "data4health-main",
        "copy_src_path": "data4health-main/vignettes",
        "copy_dest_path": "../docs/data4health"
    },
    "clim4health" : {
        "cran_url": "https://cran.r-project.org/web/packages/clim4health/index.html",
        "extracted_pkg_path": "clim4health-main",
        "copy_src_path": "clim4health-main/vignettes",
        "copy_dest_path": "../docs/clim4health"
    },
    "ghrexplore" : {
        "cran_url": "https://cran.r-project.org/web/packages/GHRexplore/index.html",
        "extracted_pkg_path": "ghrexplore-main",
        "copy_src_path": "ghrexplore-main/vignettes",
        "copy_dest_path": "../docs/GHRexplore"
    },
    "ghrmodel" : {
        "cran_url": "https://cran.r-project.org/web/packages/GHRmodel/index.html",
        "extracted_pkg_path": "ghrmodel-main",
        "copy_src_path": "ghrmodel-main/vignettes",
        "copy_dest_path": "../docs/GHRmodel"
    }
}
DATA_DIRECTORY = "../../downloaded_data/"
REPO_DOWNLOAD_URL = "https://gitlab.earth.bsc.es/ghr/{package}/-/archive/main/{package}-main.tar.gz?ref_type=heads"


def run_r_script(script_path, *args):
    if VERBOSE:
        print(f"\t\tRunning {script_path}, with args: {args}")
    resolved_path = Path(script_path).resolve()
    
    if not resolved_path.is_file():
        raise FileNotFoundError(f"R script not found: {resolved_path}")

    script_dir = resolved_path.parent

    cmd = ["Rscript", str(script_path)] + list(args)
    
    result = subprocess.run(cmd, cwd=script_dir, capture_output=True, text=True, check=False)
    
    return result.stdout, result.stderr, result.returncode

def delete_directory(dir_path):
    try:
        # Delete the directory and its contents
        shutil.rmtree(dir_path)
        print(f"\tDirectory '{dir_path}' deleted successfully.")
    except Exception as e:
        print(f"\tFailed to delete directory '{dir_path}': {e}") 

def download_tarball_from_gitlab_and_extract(module_name):
    url = REPO_DOWNLOAD_URL.format(package=module_name)
    
    if VERBOSE:
        print(f"\tDownloading module from {url}")
    cwd = os.getcwd()
    tarball_filename = os.path.join(DATA_DIRECTORY, module_name+'.tar.gz')
    cmd1 = ["mkdir", DATA_DIRECTORY]
    result = subprocess.run(cmd1, cwd=cwd, capture_output=True, text=True, check=False)

    if os.path.exists(tarball_filename):
        print(f"\tFile exists. Skipping download...")
    else:
        with open(tarball_filename, 'wb') as out_file:
            content = requests.get(url, stream=True).content
            out_file.write(content)

    cmd2 = ["R", "-e", f"install.packages('{str(tarball_filename)}', repos = NULL, type = 'source')"]
    if VERBOSE:
        print(f"\tInstalling downloaded package...")
    result = subprocess.run(cmd2, cwd=cwd, capture_output=True, text=True, check=False)

    cmd3 = ["tar", "-xzvf", str(tarball_filename), "-C", DATA_DIRECTORY]
    if VERBOSE:
        print(f"\tExtracting tarball...")
    result = subprocess.run(cmd3, cwd=cwd, capture_output=True, text=True, check=False)

    return result


def gen_md(in_generator, generator_path):
    stdout, stderr, returncode = run_r_script(in_generator, generator_path)
    if VERBOSE:
        print("\tSTDOUT:", stdout)
        print("\tTDERR:", stderr)
        print("\tReturn code:", returncode)
    if returncode == 0:
        print("\tSUCCESS")


def change_extension(file_path, new_extension):
    base_name, _ = os.path.splitext(file_path)
    new_file_path = base_name + new_extension
    os.rename(file_path, new_file_path)

def convert_all_md_to_qmd(dir_path):
    for e in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, e)):
            _, ext = os.path.splitext(e)
            if ext == ".md":
                change_extension(os.path.join(dir_path, e), ".qmd")


def move_all_generated_files(package):
    src = os.path.join(DATA_DIRECTORY, PKG_MAP[package]["copy_src_path"])
    dest = PKG_MAP[package]["copy_dest_path"]
    if VERBOSE:
        print(f"\tSource: {src}")
        print(f"\tDestination: {dest}")

    convert_all_md_to_qmd(src)

    src_path = Path(src).resolve()
    dest_path = Path(dest).resolve()
    
    if VERBOSE:
        print(f"\tCOPYING {src_path} to {dest_path}")
    shutil.copytree(src_path, dest_path, dirs_exist_ok=True, ignore=shutil.ignore_patterns('*.gitignore', '*.Rmd', '*.html'))


def move_package_readme(package):
    src_file = os.path.join(DATA_DIRECTORY, PKG_MAP[package]["extracted_pkg_path"], "README.md")
    dest_file = os.path.join(PKG_MAP[package]["copy_dest_path"], package+".qmd")

    src_path = Path(src_file).resolve()
    dest_path = Path(dest_file).resolve()
    if VERBOSE:
        print(f"\tCopying From {src_path} to {dest_path}")

    shutil.copy(src_path, dest_path)


def update_package_docs(package):

    if VERBOSE:
        print(f"FETCHING PACKAGE: {package}")
    download_tarball_from_gitlab_and_extract(package)

    try:
        pkg_dir = os.path.join(DATA_DIRECTORY, package+"-main")#PKG_MAP[package]["extracted_pkg_path"])
        if VERBOSE:
            print(f"GENERATING MARKDOWN FOR: {package}")
            print(f"\tPackage path: {pkg_dir}")
        gen_md(f"./generate_md.R", pkg_dir)

    except Exception as e:
        print(f"ERROR - Couldn't generate markdown for {package}, skipping...\n\t\tError message: {e}")

    try:
        if VERBOSE:
            print(f"MOVING GENERATED FILES FOR: {package}")
        move_all_generated_files(package)
    except Exception as e:
        print(f"ERROR - Couldn't copy generated files for {pkg} into destination, skipping...\n\t\tError message: {e}")

    try:
        if VERBOSE:
            print(f"COPYING README FOR: {package}")
        move_package_readme(package)
    except Exception as e:
        print(f"ERROR - Couldn't copy README files for {pkg} into destination, skipping...\n\t\tError message: {e}")


if __name__ == "__main__":
    VERBOSE = False

    # arguments
    parser = argparse.ArgumentParser(prog="DocumentationGeneration", description="Generates GHRTools website pages from the ghrtools gitlab")
    parser.add_argument("-p", "--packages", nargs="+", default=[])
    parser.add_argument("-v", "--verbose", action='store_true')
    parser.add_argument("-k", "--keep-data", action='store_true') # keeps the downloaded data after the script is done
    
    args = parser.parse_args()
    VERBOSE = args.verbose
    if VERBOSE:
        print(f"Args: {args}")
    target_packages = args.packages


    for pkg in target_packages:
        if pkg == "all":
            update_package_docs("ghrmodel")
            update_package_docs("ghrexplore")
            update_package_docs("data4health")
            update_package_docs("clim4health")
        else:
            if pkg == "model":
                pkg = "ghrmodel"
            if pkg == "explore":
                pkg = "ghrexplore"
            if pkg == "data" or pkg == "d4h":
                pkg = "data4health"
            if pkg == "clim" or pkg == "c4h":
                pkg = "clim4health"
                
            update_package_docs(pkg)

    if not args.keep_data:
        print(f"DELETING DATA DIRECTORY")
        delete_directory(DATA_DIRECTORY)
