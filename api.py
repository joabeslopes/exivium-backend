import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from classes.camera import Camera
from functions.plugin_manager import activate_plugin, run_plugin

#TODO variavel de ambiente
FPS = 30
active_cameras = {}

def log(mensagem: str):
    print(mensagem)

def get_channel(channel: int=None):
    all_channels = {
        1: "rtsp://localhost:8554/mystream"
    }
    if channel is None:
        return all_channels
    else:
        return all_channels[channel]

def validate_token(token: str):
    valid_tokens = {
                    "meu_token": "usuario1", 
                    "meu_token_plugin2": "plugin2",
                    }
    return token in valid_tokens

def run_cameras():
    log('Ligando cameras')
    camera_channels = get_channel()
    for channel in camera_channels:
        url = get_channel(channel)
        active_cameras[channel] = Camera(channel, url)

app = FastAPI()

@app.websocket("/ws/video/{channel}")
async def video_stream(websocket: WebSocket, token: str, channel: int):
    if not validate_token(token):
        log("[ERRO] Token invalido")
        raise WebSocketDisconnect(code=1008, reason="Token inválido")

    if channel not in active_cameras:
        log(f"[ERRO] Camera {channel} nao encontrada")
        raise WebSocketDisconnect(code=1008, reason="Camera nao encontrada")

    camera = active_cameras[channel]

    if not camera.isRunning():
        log(f"Camera {channel} nao está funcionando")
        raise WebSocketDisconnect(code=1008, reason="Camera nao está funcionando")

    await websocket.accept()
    log("Cliente conectado")

    try:
        while camera.isRunning():
            image = camera.get_image()
            if image:
                await websocket.send_bytes(image)
            await asyncio.sleep(1 / FPS)
    except WebSocketDisconnect:
        log("Cliente desconectado")

@app.websocket("/ws/results")
async def result_receiver(websocket: WebSocket, token: str):
    if not validate_token(token):
        log("[ERRO] Token invalido")
        raise WebSocketDisconnect(code=1008, reason="Token inválido")

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            log(f"Cliente enviou: {data}")
    except WebSocketDisconnect:
        log("Cliente desconectado")


if __name__ == 'api':
    run_cameras()
    activate_plugin('plugins/exemplo')
    run_plugin('plugins/exemplo', camera_id=1)