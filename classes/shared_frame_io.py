import numpy as np
import cv2
from multiprocessing import shared_memory, Lock

#TODO variavel de ambiente
FRAME_WIDTH = 640
FRAME_HEIGHT = 360
JPEG_QUALITY = 70

class MemoryConnector:
    def __init__(self, channel: int):
        self.channel = channel
        self.name = f"camera_{channel}"
        self.shape = (FRAME_HEIGHT, FRAME_WIDTH, 3)
        self.dtype = np.uint8
        self.frame_size = int( np.prod(self.shape) * np.dtype(self.dtype).itemsize )
        self.running = False
        self.lock = Lock()
    
    def isRunning(self):
        return self.running


class FrameReader(MemoryConnector):
    def start(self):
        try:
            self.shm = shared_memory.SharedMemory(name=self.name, create=False, size=self.frame_size)
            self.array = np.ndarray(self.shape, dtype=self.dtype, buffer=self.shm.buf)
            self.running = True
        
        except FileNotFoundError:
            print(f"Memória compartilhada não encontrada: {self.name}")
            raise
        except Exception as e:
            print(f"Erro ao conectar na shared memory {self.name}: {e}")
            raise

    def close(self):
        if self.running:
            try:
                self.shm.close()
                self.running = False
            except Exception as e:
                print(f"Erro ao fechar shared memory: {e}")

    def read(self) -> np.ndarray:
        with self.lock:
            return self.array.copy()

    def get_image(self) -> bytes | None:
        try:
            frame = self.read()
            encoded, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
            if encoded:
                return buffer.tobytes()
        except Exception as e:
            print(f"[ERRO] Falha ao codificar frame da câmera {self.name}: {e}")
        return None


class FrameWriter(MemoryConnector):
    def start(self):
        try:
            self.shm = shared_memory.SharedMemory(name=self.name, create=True, size=self.frame_size)
            self.array = np.ndarray(self.shape, dtype=self.dtype, buffer=self.shm.buf)
            self.running = True
        except FileExistsError:
            print(f"Memória compartilhada ja foi criada: {self.name}")
            raise
        except Exception as e:
            print(f"Erro ao conectar na shared memory {self.name}: {e}")
            raise

    def write(self, frame: np.ndarray):
        with self.lock:
            np.copyto(self.array, frame)

    def close(self):
        if self.running:
            try:
                self.shm.close()
                self.shm.unlink()
                self.running = False
            except Exception as e:
                print(f"Erro ao fechar shared memory: {e}")