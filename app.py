import cv2
import asyncio
import threading
import time
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

JPEG_QUALITY = 60
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 60

valid_tokens = {
                "meu_token": "usuario1", 
                "meu_token_plugin2": "plugin2",
                }

class Camera:
    def __init__(self, source=0):
        self.cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.frame = None
        self.running = False
        self.thread = threading.Thread(target=self._capture, daemon=True)
        self.thread.start()

    def _capture(self):
        self.running = True
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
                self.frame = buffer.tobytes()
            time.sleep(1 / FPS)

    def get_frame(self):
        return self.frame

    def stop(self):
        self.running = False
        self.cap.release()

camera = Camera(0)

@app.websocket("/ws/video")
async def video_stream(websocket: WebSocket, token: str):
    if token not in valid_tokens:
        await websocket.close()
        raise HTTPException(status_code=401, detail="Token inválido")

    await websocket.accept()
    print("cliente conectado")
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