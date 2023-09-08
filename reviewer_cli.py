import click

from github_handler import fetch_prs_with_labels
from grayskull_handler import run_grayskull
from file_comparator import compare_files, compare_yaml_files
from maintainer_checker import check_maintainers_in_comments
from license_checker import check_license_in_repo

@click.group()
def cli():
    pass

@click.command()
@click.argument('token')
@click.argument('repo_name')
@click.argument('labels', nargs=-1)
def fetch_prs(token, repo_name, labels):
    prs = fetch_prs_with_labels(token, repo_name, labels)
    for pr in prs:
        click.echo(f"Fetched PR: {pr.title}")

@click.command()
@click.argument('package_name')
@click.argument('output_path')
def grayskull(package_name, output_path):
    run_grayskull(package_name, output_path)
    click.echo(f"Grayskull run for package: {package_name}")

@click.command()
@click.argument('file1')
@click.argument('file2')
def compare(file1, file2):
    result = compare_files(file1, file2)
    click.echo(f"Files are {'identical' if result else 'different'}")

@click.command()
@click.argument('file1')
@click.argument('file2')
def compare_yaml(file1, file2):
    result = compare_yaml_files(file1, file2)
    click.echo(f"YAML files are {'identical' if result else 'different'}")

# Additional commands for other functions can be added similarly

cli.add_command(fetch_prs)
cli.add_command(grayskull)
cli.add_command(compare)
cli.add_command(compare_yaml)

if __name__ == '__main__':
    cli()
