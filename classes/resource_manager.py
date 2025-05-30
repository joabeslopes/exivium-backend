from classes.camera import Camera
from classes.plugin import Plugin
from functions.channels import get_channel
import atexit

class ResourceManager:
    def __init__(self):
        self.cameras: dict[int, Camera] = {}
        self.plugins: dict[tuple, Plugin] = {}
        self.results: dict[tuple, bytes] = {}
        atexit.register(self.stop_all)

    def start_camera(self, channel: int):
        url = get_channel(channel)
        if url is None:
            print(f"Canal {channel} inválido")
            return
        camera = Camera(channel, url)
        if camera.isRunning():
            self.cameras[channel] = camera
            print(f"Câmera {channel} iniciada")

    def stop_camera(self, channel: int):
        camera = self.cameras.pop(channel, None)
        if camera:
            camera.stop()
            print(f"Câmera {channel} parada")

    def start_plugin(self, plugin_name: str, channel: int, token: str):
        key = (plugin_name, channel)
        if key in self.plugins:
            print(f"Plugin {key} já está em execução")
            return
        plugin = Plugin(plugin_name, channel, token)
        self.plugins[key] = plugin
        print(f"Plugin {key} iniciado")

    def stop_plugin(self, plugin_name: str, channel: int):
        key = (plugin_name, channel)
        plugin = self.plugins.pop(key, None)
        if plugin:
            plugin.stop()
            print(f"Plugin {key} parado")

    def set_result(self, key: tuple, image: bytes):
        self.results[key] = image

    def get_result(self, key: tuple) -> bytes:
        return self.results[key]

    def stop_all(self):
        for cam_id in list(self.cameras.keys()):
            self.stop_camera(cam_id)
        for key in list(self.plugins.keys()):
            plugin_name = key[0]
            channel = key[1]
            self.stop_plugin(plugin_name, channel)
        print("Todos os recursos foram encerrados")

    def get_all_cameras(self) -> list:
        allCameras = list(self.cameras.keys())
        return allCameras