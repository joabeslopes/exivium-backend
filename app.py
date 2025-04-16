import cv2
import asyncio
import threading
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

JPEG_QUALITY = 60
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30

valid_tokens = {
                "meu_token": "usuario1", 
                "meu_token_plugin2": "plugin2",
                }

camera_channels = {
    1: "rtsp://localhost:8554/mystream"
}

active_cameras = {}

class Camera:
    def __init__(self, channel: int):
        self.frame = None
        self.running = False

        self.url = camera_channels[channel]
        if not self.url:
            print("[ERRO CAMERA] Canal inválido.")
            return

        self.cap = cv2.VideoCapture(self.url)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)
        self.thread = threading.Thread(target=self._capture, daemon=True)
        self.thread.start()

    def _capture(self):
        self.running = True
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
                self.frame = buffer.tobytes()

    def get_frame(self):
        return self.frame

    def stop(self):
        self.running = False
        self.cap.release()


for channel in camera_channels:
    active_cameras[channel] = Camera(channel)

@app.websocket("/ws/video/{channel}")
async def video_stream(websocket: WebSocket, token: str, channel: int):
    if token not in valid_tokens:
        raise WebSocketDisconnect(code=1008, reason="Token inválido")

    if channel not in active_cameras:
        raise WebSocketDisconnect(code=1008, reason="Camera nao encontrada")

    await websocket.accept()
    print("cliente conectado")

    camera = active_cameras[channel]

    if not camera.running:
        raise WebSocketDisconnect(code=1008, reason="Camera nao está funcionando")

    try:
        while camera.running:
            frame = camera.get_frame()
            if frame:
                await websocket.send_bytes(frame)
            await asyncio.sleep(1 / FPS)
    except WebSocketDisconnect:
        print("cliente desconectado")

@app.websocket("/ws/results")
async def result_receiver(websocket: WebSocket, token: str):
    if token not in valid_tokens:
        raise WebSocketDisconnect(code=1008, reason="Token inválido")

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Cliente enviou: {data}")
    except WebSocketDisconnect:
        print("Cliente desconectado")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)