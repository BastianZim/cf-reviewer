import subprocess
import json
import yaml

def fetch_prs():
    # Read configuration from YAML file
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    repo_name = config['repository_name']
    labels = config['labels']
    number_of_prs = config['number_of_prs']
    label_args = " ".join([f"--label {label}" for label in labels])

    command = f"gh pr list -R {repo_name} -s open --json number,title,url,createdAt {label_args}"
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True, text=True)
    prs_json = result.stdout

    # Check if the result is empty or not a valid JSON
    if prs_json.strip() == '':
        return []

    prs = json.loads(prs_json)

    # Sort by creation date and take the first number_of_prs
    sorted_prs = sorted(prs, key=lambda x: x['createdAt'])[:number_of_prs]
    
    return sorted_prs


if __name__ == "__main__":
    prs = fetch_prs()
    for pr in prs:
        print(f"PR Number: {pr['number']}, Title: {pr['title']}, URL: {pr['url']}")
