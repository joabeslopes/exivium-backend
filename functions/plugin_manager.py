import os
import shutil
import subprocess
import sys
import venv

def get_venv_dir(plugin_path: str):
    return os.path.join(plugin_path, '.venv')

def get_venv_python(venv_dir: str):
    if os.name == 'nt':
        return os.path.join(venv_dir, 'Scripts', 'python.exe')
    else:
        return os.path.join(venv_dir, 'bin', 'python')

def deactivate_plugin(plugin_path: str):
    # Apagar ambiente virtual anterior (se existir)
    if os.path.exists(venv_dir):
        print(f"[INFO] Removendo ambiente virtual existente em {venv_dir}")
        shutil.rmtree(venv_dir)

def activate_plugin(plugin_path: str):
    venv_dir = get_venv_dir(plugin_path)

    # Se ja existir o ambiente virtual, nao cria de novo
    if os.path.exists(venv_dir):
        print(f"[INFO] Ja existe ambiente virtual em {venv_dir}, pulando ativação.")
        return

    # Criar novo ambiente virtual
    print(f"[INFO] Criando novo ambiente virtual em {venv_dir}")
    venv.EnvBuilder(with_pip=True).create(venv_dir)

    # Instalar dependências
    venv_python = get_venv_python(venv_dir)
    requirements_path = os.path.join(plugin_path, 'requirements.txt')
    if os.path.exists(requirements_path):
        print(f"[INFO] Instalando dependências do {requirements_path}")
        subprocess.run([venv_python, '-m', 'pip', 'install', '-r', requirements_path], check=True)
    else:
        print(f"[INFO] Nenhum requirements.txt encontrado, pulando instalação.")

def run_plugin(plugin_path: str, camera_id: int):
    venv_dir = get_venv_dir(plugin_path)

    if not os.path.exists(venv_dir):
        print(f"[ERRO] Ambiente virtual não encontrado em {venv_dir}. Ative o plugin primeiro.")
        return

    venv_python = get_venv_python('.venv') # Para não duplicar o caminho absoluto
    plugin_main = 'main.py'

    print(f"[INFO] Iniciando plugin {plugin_path} com camera_id={camera_id}")
    subprocess.Popen(
        [venv_python, plugin_main, str(camera_id)],
        cwd=os.path.join(plugin_path)
    )