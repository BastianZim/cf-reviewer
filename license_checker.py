import requests

def check_license_in_repo(repo_url, license_file):
    license_url = f"{repo_url}/blob/master/{license_file}"
    response = requests.get(license_url)
    return response.status_code == 200
