import numpy as np
from multiprocessing import shared_memory
import threading
import atexit

#TODO variavel de ambiente
FRAME_WIDTH = 640
FRAME_HEIGHT = 360

class FrameWriter:
    def __init__(self, camera_id: int):
        self.name = f"camera_{camera_id}"
        self.shape = (FRAME_HEIGHT, FRAME_WIDTH, 3)
        self.dtype = np.uint8
        self.frame_size = int( np.prod(self.shape) * np.dtype(self.dtype).itemsize )

        try:
            self.shm = shared_memory.SharedMemory(name=self.name, create=True, size=self.frame_size)
        except FileExistsError:
            self.shm = shared_memory.SharedMemory(name=self.name, create=False, size=self.frame_size)

        self.array = np.ndarray(self.shape, dtype=self.dtype, buffer=self.shm.buf)
        self.lock = threading.Lock()

        atexit.register(self.close)

    def write(self, frame: np.ndarray):
        with self.lock:
            np.copyto(self.array, frame)

    def close(self):
        self.shm.close()
        self.shm.unlink()


class FrameReader:
    def __init__(self, camera_id: int):
        self.name = f"camera_{camera_id}"
        self.shape = (FRAME_HEIGHT, FRAME_WIDTH, 3)
        self.dtype = np.uint8
        self.frame_size = int( np.prod(self.shape) * np.dtype(self.dtype).itemsize )

        self.shm = shared_memory.SharedMemory(name=self.name)
        self.array = np.ndarray(self.shape, dtype=self.dtype, buffer=self.shm.buf)
        self.lock = threading.Lock()

        atexit.register(self.close)

    def read(self) -> np.ndarray:
        with self.lock:
            return self.array.copy()

    def close(self):
        self.shm.close()