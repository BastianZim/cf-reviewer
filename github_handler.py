from github import Github

def fetch_prs_with_labels(token, repo_name, labels):
    g = Github(token)
    repo = g.get_repo(repo_name)
    prs = repo.get_pulls(state='open', sort='created')
    filtered_prs = [pr for pr in prs if all(label.name in labels for label in pr.labels)]
    return filtered_prs
