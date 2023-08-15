def check_maintainers_in_comments(pr, maintainers):
    comments = pr.get_issue_comments()
    for maintainer in maintainers:
        if any(maintainer in comment.body for comment in comments):
            return True
    return False
