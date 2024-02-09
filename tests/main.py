import os
import sys
import pytest
import subprocess
from pathlib import Path

# base path resolving
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

DATA_PATH = "tests/data"

directories = list(filter(
    lambda x: os.path.isdir(BASE_DIR / DATA_PATH / x),
    os.listdir(BASE_DIR / DATA_PATH)
))


@pytest.mark.parametrize("directory", directories)
def test_with_directory(directory):
    path_to_dir = BASE_DIR / "tests/data/" / directory
    command = f"python3 {BASE_DIR / 'src/main.py'} -i {path_to_dir / 'in.txt'} -o {path_to_dir / 'out_actual.txt'}"
    subprocess.call((command), shell=True)
    # checking
    with open(path_to_dir / "out.txt") as output_expected_file:
        output_expected = output_expected_file.read().strip()

    with open(path_to_dir / "out_actual.txt") as output_actual_file:
        output_actual = output_actual_file.read().strip()

    assert output_expected == output_actual, "Results do not match!"