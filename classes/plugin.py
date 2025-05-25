import os
import shutil
import subprocess
import sys
import venv
from functions.dir_manager import get_venv_dir, get_venv_python
import signal


class Plugin:
    def __init__(self, plugin_name: str, channel: int, token: str):
        self.plugin_name = plugin_name
        self.channel = str(channel)
        self.token = token
        self.path = f'plugins/{plugin_name}'
        self.venv_dir = get_venv_dir(self.path)
        self.venv_python = get_venv_python(self.venv_dir)
        self.process = self.start()

    def start(self):
        self.activate()

        venv_python = get_venv_python('.venv') # Para não duplicar o caminho absoluto
        plugin_main = 'main.py'

        print(f"[INFO] Iniciando plugin {self.path} com channel={self.channel}")
        
        return subprocess.Popen(
            [venv_python, plugin_main, self.plugin_name ,self.channel, self.token],
            cwd=os.path.join(self.path)
        )

    def stop(self):
        print(f"[INFO] Encerrando instancia {self.plugin_name}-{self.channel}")

        if self.process.poll() is None:  # ainda está rodando
            self.process.send_signal(signal.SIGTERM)
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

    def deactivate(self):
        # Apagar ambiente virtual anterior (se existir)
        if os.path.exists(self.venv_dir):
            print(f"[INFO] Removendo ambiente virtual existente em {self.venv_dir}")
            shutil.rmtree(self.venv_dir)

    def activate(self):
        # Se ja existir o ambiente virtual, nao cria de novo
        if os.path.exists(self.venv_dir):
            print(f"[INFO] Ja existe ambiente virtual em {self.venv_dir}, pulando ativação.")
            return

        # Criar novo ambiente virtual
        print(f"[INFO] Criando novo ambiente virtual em {self.venv_dir}")
        venv.EnvBuilder(with_pip=True).create(self.venv_dir)

        # Instalar dependências
        venv_python = get_venv_python(self.venv_dir)
        requirements_path = os.path.join(self.path, 'requirements.txt')
        if os.path.exists(requirements_path):
            print(f"[INFO] Instalando dependências do {requirements_path}")
            subprocess.run([venv_python, '-m', 'pip', 'install', '-r', requirements_path], check=True)
        else:
            print(f"[INFO] Nenhum requirements.txt encontrado, pulando instalação.")
