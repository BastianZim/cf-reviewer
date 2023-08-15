import subprocess
import json

def fetch_prs():
    repo_name = "conda-forge/staged-recipes"
    labels = ["python", "review-requested"]
    label_query = " ".join([f"label:{label}" for label in labels])

    command = f"gh pr list -R {repo_name} -s open --json number,title,url --label {label_query}"
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True, text=True)
    prs_json = result.stdout

    prs = json.loads(prs_json)
    return prs
