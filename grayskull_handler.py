import subprocess

def run_grayskull(package_name, output_path):
    command = f"grayskull pypi -d --output {output_path} --strict-conda-forge {package_name}"
    subprocess.run(command, shell=True)
