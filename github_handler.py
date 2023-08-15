import subprocess
import json
import yaml
import jinja2
import requests


def fetch_prs():
    """Fetch PRs with package names from the specified repository."""
    config = _read_config()
    sorted_prs = _get_sorted_prs(config)
    extended_prs = _extract_package_names(sorted_prs, config['repository_name'])
    return extended_prs


def _read_config():
    """Read configuration from the YAML file."""
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    return config


def _get_sorted_prs(config):
    """Get sorted PRs based on the configuration."""
    repo_name = config['repository_name']
    label_args = " ".join([f"--label {label}" for label in config['labels']])
    command = f"gh pr list -R {repo_name} -s open --json number,title,url,createdAt {label_args}"
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True, text=True)
    prs_json = result.stdout.strip()
    prs = json.loads(prs_json) if prs_json else []
    sorted_prs = sorted(prs, key=lambda x: x['createdAt'])[:config['number_of_prs']]
    return sorted_prs


def _extract_package_names(sorted_prs, repo_name):
    """Extract package names from the sorted PRs."""
    extended_prs = []
    for pr in sorted_prs:
        pr_number = pr['number']
        meta_yaml_files = _get_meta_yaml_files(pr_number, repo_name)
        for meta_yaml_file in meta_yaml_files:
            meta_yaml_content = _download_meta_yaml_content(pr_number, repo_name, meta_yaml_file)
            package_name = _extract_package_name(meta_yaml_content)
            pr_with_package = pr.copy()
            pr_with_package['package_name'] = package_name
            extended_prs.append(pr_with_package)
    return extended_prs


def _get_meta_yaml_files(pr_number, repo_name):
    """Get meta.yaml files from the specified PR number and repository name."""
    command = f"gh pr diff {pr_number} -R {repo_name} --name-only"
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True, text=True)
    added_files = result.stdout.splitlines()
    meta_yaml_files = [f for f in added_files if f.startswith('recipes/') and f.endswith('/meta.yaml')]
    return meta_yaml_files


def _download_meta_yaml_content(pr_number, repo_name, meta_yaml_file):
    """Download the content of the specified meta.yaml file."""
    download_url = f"https://raw.githubusercontent.com/{repo_name}/pull/{pr_number}/head/{meta_yaml_file}"
    response = requests.get(download_url)
    return response.text


def _extract_package_name(meta_yaml_content):
    """Extract the package name from the provided meta.yaml content."""
    template = jinja2.Template(meta_yaml_content)
    rendered_yaml = template.render()
    package_info = yaml.safe_load(rendered_yaml)
    package_name = package_info['package']['name']
    return package_name


if __name__ == "__main__":
    prs = fetch_prs()
    for pr in prs:
        print(f"PR Number: {pr['number']}, Title: {pr['title']}, URL: {pr['url']}")
