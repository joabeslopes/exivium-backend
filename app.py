import cv2
import asyncio
import threading
import time
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import av

app = FastAPI()

JPEG_QUALITY = 60
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 60

valid_tokens = {
                "meu_token": "usuario1", 
                "meu_token_plugin2": "plugin2",
                }

camera_channels = {
    1: "rtsp://localhost:554/live"
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

        try:
            self.container = av.open(self.url, timeout=5)  # timeout em segundos
        except Exception as e:
            print(f"[ERRO CAMERA] Falha ao abrir a câmera: {e}")
            return

        self.stream = self.container.streams.video[0]
        self.stream.thread_type = "AUTO"

        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        try:
            for frame in self.container.decode(video=0):
                if not self.running:
                    break

                # Converte para array BGR (OpenCV)
                img = frame.to_ndarray(format="bgr24")

                # Redimensiona (opcional)
                img = cv2.resize(img, (FRAME_WIDTH, FRAME_HEIGHT))

                success, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
                if success:
                    self.frame = buffer.tobytes()

        except Exception as e:
            print(f"[ERRO CAPTURA] {e}")
            self.running = False

    def get_frame(self):
        return self.frame

    def stop(self):
        self.running = False
        try:
            self.container.close()
        except Exception:
            pass


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
        await websocket.close()
        raise HTTPException(status_code=401, detail="Token inválido")

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Cliente enviou: {data}")
    except WebSocketDisconnect:
        print("Cliente desconectado")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)