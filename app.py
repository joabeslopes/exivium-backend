import cv2
import asyncio
import threading
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import atexit

JPEG_QUALITY = 70
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
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


class Camera:
    def __init__(self, channel: int):
        self.frame = None
        self.running = False
        self.channel = channel

        self.url = get_channel(channel)
        if self.url is None:
            log(f"[ERRO] Canal {channel} nao existe")
            return

        self.cap = cv2.VideoCapture(self.url)

        self.running = self.cap.isOpened()
        if not self.running:
            log(f"[ERRO] Camera {self.url} invalida")
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)
        self.thread = threading.Thread(target=self._capture, daemon=True)
        self.thread.start()
        atexit.register(self.stop)

    def _capture(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                encoded, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
                if encoded:
                    self.frame = buffer.tobytes()
        self.running = False

    def get_frame(self):
        return self.frame

    def stop(self):
        log(f"Parando camera {self.channel}")
        self.running = False
        self.cap.release()


def run_cameras():
    log('Ligando cameras')
    camera_channels = get_channel()
    for channel in camera_channels:
        active_cameras[channel] = Camera(channel)

app = FastAPI()

@app.websocket("/ws/video/{channel}")
async def video_stream(websocket: WebSocket, token: str, channel: int):
    if not validate_token(token):
        log("[ERRO] Token invalido")
        raise WebSocketDisconnect(code=1008, reason="Token inválido")

    if channel not in active_cameras:
        log(f"[ERRO] Camera {channel} nao encontrada")
        raise WebSocketDisconnect(code=1008, reason="Camera nao encontrada")

    await websocket.accept()
    log("Cliente conectado")

    camera = active_cameras[channel]

    if not camera.running:
        log(f"Camera {channel} nao está funcionando")
        raise WebSocketDisconnect(code=1008, reason="Camera nao está funcionando")

    try:
        while camera.running:
            frame = camera.get_frame()
            if frame:
                await websocket.send_bytes(frame)
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


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
elif __name__ == "app":
    run_cameras()