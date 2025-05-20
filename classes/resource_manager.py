from classes.camera import Camera
from classes.plugin import Plugin
import atexit

class ResourceManager:
    def __init__(self):
        self.cameras: dict[int, Camera] = {}
        self.plugins: dict[tuple, Plugin] = {}
        atexit.register(self.stop_all)

    def get_channel(self, channel: int = None):
        all_channels = {
            1: "rtsp://localhost:8554/mystream"
        }
        if channel is None:
            return all_channels
        return all_channels.get(channel)

    def start_camera(self, channel: int):
        url = self.get_channel(channel)
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

    def start_plugin(self, plugin_name: str, channel: int):
        key = (plugin_name, channel)
        if key in self.plugins:
            print(f"Plugin {key} já está em execução")
            return
        plugin = Plugin(plugin_name, channel)
        self.plugins[key] = plugin
        print(f"Plugin {key} iniciado")

    def stop_plugin(self, plugin_name: str, channel: int):
        key = (plugin_name, channel)
        plugin = self.plugins.pop(key, None)
        if plugin:
            plugin.stop()
            print(f"Plugin {key} parado")

    def stop_all(self):
        for cam_id in list(self.cameras.keys()):
            self.stop_camera(cam_id)
        for key in list(self.plugins.keys()):
            plugin_name = key[0]
            channel = key[1]
            self.stop_plugin(plugin_name, channel)
        print("Todos os recursos foram encerrados")