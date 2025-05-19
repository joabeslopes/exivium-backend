import numpy as np
from multiprocessing import shared_memory
import threading
import atexit

#TODO variavel de ambiente
FRAME_WIDTH = 640
FRAME_HEIGHT = 360

class MemoryConnector:
    def __init__(self, camera_id: int):
        self.name = f"camera_{camera_id}"
        self.shape = (FRAME_HEIGHT, FRAME_WIDTH, 3)
        self.dtype = np.uint8
        self.frame_size = int( np.prod(self.shape) * np.dtype(self.dtype).itemsize )
        self.running = False
    
    def isRunning(self):
        return self.running

    def start(self):
        try:
            self.shm = shared_memory.SharedMemory(name=self.name, create=True, size=self.frame_size)
            self.running = True
        except FileExistsError:
            self.shm = shared_memory.SharedMemory(name=self.name, create=False, size=self.frame_size)
            self.running = True
        except FileNotFoundError as notFound:
            print(f'Nao encontrada shared memory {self.name}')
            raise notFound
        except Exception as e:
            print(f'Erro ao conectar na shared memory {self.name}')
            print(e)
            raise e

        self.array = np.ndarray(self.shape, dtype=self.dtype, buffer=self.shm.buf)
        self.lock = threading.Lock()

        atexit.register(self.close)

        return self.running

    def close(self):
        if self.running:
            try:
                self.shm.close()
            except Exception as e:
                print(e)


class FrameWriter(MemoryConnector):
    def write(self, frame: np.ndarray):
        with self.lock:
            np.copyto(self.array, frame)

    def close(self):
        if self.running:
            try:
                self.shm.close()
                self.shm.unlink()
            except Exception as e:
                print(e)


class FrameReader(MemoryConnector):
    def read(self) -> np.ndarray:
        with self.lock:
            return self.array.copy()