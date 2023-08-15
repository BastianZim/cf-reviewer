import subprocess
import json

def fetch_prs():
    repo_name = "conda-forge/staged-recipes"
    labels = ["python", "review-requested"]
    label_args = " ".join([f"--label {label}" for label in labels])

    # Include the createdAt field to sort by creation date
    command = f"gh pr list -R {repo_name} -s open --json number,title,url,createdAt {label_args}"
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True, text=True)
    prs_json = result.stdout

    # Check if the result is empty or not a valid JSON
    if prs_json.strip() == '':
        return []

    prs = json.loads(prs_json)

    # Sort by creation date and take the first 20
    sorted_prs = sorted(prs, key=lambda x: x['createdAt'])[:20]
    
    return sorted_prs

if __name__ == "__main__":
    prs = fetch_prs()
    for pr in prs:
        print(f"PR Number: {pr['number']}, Title: {pr['title']}, URL: {pr['url']}")
