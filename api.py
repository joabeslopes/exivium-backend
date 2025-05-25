import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from classes.camera import Camera
from classes.resource_manager import ResourceManager
from functions.log import log
from functions.tokens import get_token_info

#TODO variavel de ambiente
FPS = 30

app = FastAPI()
resource_manager = ResourceManager()

@app.websocket("/ws/video/{channel}")
async def video_stream(websocket: WebSocket, token: str, channel: int):
    info = await get_token_info(token)
    if not info:
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

@app.websocket("/ws/results/{plugin_name}/{channel}")
async def result_receiver(websocket: WebSocket, plugin_name: str, channel: int, token: str):
    info = await get_token_info(token)
    if not info:
        log("[ERRO] Token invalido")
        raise WebSocketDisconnect(code=1008, reason="Token inválido")

    key = (plugin_name, channel)

    if not key in resource_manager.plugins:
        log("[ERRO] Plugin invalido")
        raise WebSocketDisconnect(code=1008, reason="Plugin inválido")

    await websocket.accept()

    if info["role"] == "plugin":
        try:
            while True:
                data = await websocket.receive_bytes()
                resource_manager.set_result(key, data)
                await asyncio.sleep(1 / FPS)
        except WebSocketDisconnect:
            log("Plugin desconectado")
    else:
        try:
            while True:
                data = resource_manager.get_result(key)
                await websocket.send_bytes(data)
                await asyncio.sleep(1 / FPS)
        except WebSocketDisconnect:
            log("Usuario desconectado")

@app.get("/api/allCameras")
async def get_all_cameras(token: str):
    info = await get_token_info(token)
    if not info:
        log("[ERRO] Token invalido")
        raise HTTPException(status_code=401, detail="Token invalido")

    return resource_manager.get_all_cameras()

if __name__ == 'api':
    resource_manager.start_camera(1)
    resource_manager.start_camera(2)
    resource_manager.start_plugin("exemplo", 1, "meu_token_exemplo")