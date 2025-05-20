import os

def get_venv_dir(path: str):
    return os.path.join(path, '.venv')

def get_venv_python(path: str):
    if os.name == 'nt':
        return os.path.join(path, 'Scripts', 'python.exe')
    else:
        return os.path.join(path, 'bin', 'python')