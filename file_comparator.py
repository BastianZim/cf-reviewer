import filecmp
import yaml

def compare_files(file1, file2):
    return filecmp.cmp(file1, file2)

def compare_yaml_files(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        yaml1 = yaml.safe_load(f1)
        yaml2 = yaml.safe_load(f2)
    return yaml1 == yaml2
