import cv2
import threading
from classes.shared_frame_io import FrameWriter
import atexit

#TODO variavel de ambiente
JPEG_QUALITY = 70
FRAME_WIDTH = 640
FRAME_HEIGHT = 360
FPS = 30

class Camera:
    def __init__(self, channel: int, url: str):
        self.frame = None
        self.channel = channel
        self.url = url
        self.cap = cv2.VideoCapture(self.url)

        if not self.cap.isOpened():
            print(f"[ERRO] Camera {self.url} invalida")
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)

        self.size_offset = 0

        real_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        real_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if (real_width != FRAME_WIDTH or real_height != FRAME_HEIGHT):
            if (real_width > FRAME_WIDTH or real_height > FRAME_HEIGHT):
                self.size_offset = 1
            else:
                self.size_offset = -1

        self.writer = FrameWriter(channel)

        self.thread = threading.Thread(target=self._capture, daemon=True)
        self.thread.start()
        atexit.register(self.stop)

    def isRunning(self):
        return self.cap.isOpened()

    def _capture(self):
        try:
            self.writer.start()
        except Exception as e:
            self.stop()
            return

        while self.isRunning():
            readed, frame = self.cap.read()
            if readed:
                match self.size_offset:
                    case 1: # Downscale 
                        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT), interpolation=cv2.INTER_AREA)
                    case -1: # Upscale
                        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT), interpolation=cv2.INTER_LINEAR )

                self.writer.write(frame)
                self.frame = frame

    def get_frame(self):
        if not self.isRunning():
            return None
        return self.frame

    def get_image(self):
        if not self.isRunning():
            return None

        image = None
        frame = self.get_frame()
        try:
            encoded, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
            if encoded:
                image = buffer.tobytes()
        except cv2.error as e:
            print(f"Encode error: {e}")
        return image

    def stop(self):
        print(f"Parando camera {self.channel}")
        self.cap.release()