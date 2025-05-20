import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from classes.camera import Camera
from classes.resource_manager import ResourceManager
from functions.log import log
from functions.tokens import validate_token

#TODO variavel de ambiente
FPS = 30

app = FastAPI()
resource_manager = ResourceManager()

@app.websocket("/ws/video/{channel}")
async def video_stream(websocket: WebSocket, token: str, channel: int):
    if not validate_token(token):
        log("[ERRO] Token invalido")
        raise WebSocketDisconnect(code=1008, reason="Token inválido")

    camera: Camera = resource_manager.cameras.get(channel)
    if not camera or not camera.isRunning():
        raise WebSocketDisconnect(code=1008, reason="Câmera não disponível")

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
    resource_manager.start_camera(1)
    resource_manager.start_plugin("exemplo", 1)