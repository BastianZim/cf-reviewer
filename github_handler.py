"""Get all PRs from GitHub."""
import subprocess
import json
import yaml
from jinja2 import Template, Undefined
import os
import requests


def fetch_prs():
    """Fetch PRs with package names from the specified repository."""
    config = _read_config()
    token = os.environ.get("CF_REVIEWER")
    sorted_prs = _get_sorted_prs(config)
    extended_prs = _extract_package_names(sorted_prs, config['repository_name'], token)
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

    os.environ['CLICOLOR_FORCE'] = '0'

    result = subprocess.check_output(command, shell=True, text=True)
    prs_json = result.strip()

    # Check if the output is not empty and is a valid JSON
    if prs_json and prs_json != "null":
        prs = json.loads(prs_json)
    else:
        prs = []

    sorted_prs = sorted(prs, key=lambda x: x['createdAt'])[:config['number_of_prs']]
    return sorted_prs


def _extract_package_names(sorted_prs, repo_name, token):
    """Extract package names from the sorted PRs."""
    extended_prs = []
    for pr in sorted_prs:
        pr_number = pr['number']
        meta_yaml_files = _get_meta_yaml_files(pr_number, repo_name)
        for meta_yaml_file in meta_yaml_files:
            meta_yaml_content = _download_meta_yaml_content(pr_number, repo_name, meta_yaml_file, token)
            package_name = _extract_package_name(meta_yaml_content)
            pr_with_package = pr.copy()
            pr_with_package['package_name'] = package_name
            extended_prs.append(pr_with_package)
    return extended_prs


def _get_meta_yaml_files(pr_number, repo_name):
    """Get meta.yaml files from the specified PR number and repository name."""
    command = f"gh pr diff {pr_number} -R {repo_name} --name-only"
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True, text=True, check=True)
    added_files = result.stdout.splitlines()
    meta_yaml_files = [f for f in added_files if f.startswith('recipes/') and f.endswith('/meta.yaml')]
    return meta_yaml_files


def _download_meta_yaml_content(pr_number, repo_name, meta_yaml_file, token):
    """Download the content of the specified meta.yaml file."""
    print("Trying to download:", pr_number)
    # Get the PR details using the GitHub API
    pr_url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}"
    headers = {'Authorization': f'token {token}'}
    pr_response = requests.get(pr_url, headers=headers)
    pr_data = pr_response.json()

    # Get the ref (SHA) of the specific commit in the pull request
    ref = pr_data['head']['sha']

    # Construct the URL to download the raw content of the meta.yaml file
    download_url = f"https://raw.githubusercontent.com/{repo_name}/{ref}/{meta_yaml_file}"
    response = requests.get(download_url)
    return response.text


class SilentUndefined(Undefined):
    """Ignore undefined variables."""

    def _fail_with_undefined_error(self, *args, **kwargs):
        return ''

    __str__ = __call__ = __getattr__ = _fail_with_undefined_error


def _render_jinja_template(template_content):
    """Render the provided Jinja template, ignoring undefined variables."""
    template = Template(template_content, undefined=SilentUndefined)
    return template.render()


def _extract_package_name(meta_yaml_content):
    """Extract the package name from a meta.yaml file."""
    rendered_content = _render_jinja_template(meta_yaml_content)
    yaml_content = yaml.safe_load(rendered_content)
    return yaml_content['package']['name']


# if __name__ == "__main__":
#     prs = fetch_prs()
#     for pr in prs:
#         print(f"PR Number: {pr['number']}, Title: {pr['title']}, URL: {pr['url']}")
