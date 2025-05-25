from shared_frame_io import FrameReader
import cv2
import sys
import asyncio
import numpy as np
import websockets

#TODO variavel de ambiente
JPEG_QUALITY = 70
FPS = 30

async def send_image(websocket, frame: np.ndarray):
    encoded, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    if encoded:
        image = buffer.tobytes()
        await websocket.send(image)
    else:
        raise ValueError("Falha ao codificar imagem.")


async def main(plugin_name, channel, token):
    print(f'Rodando plugin exemplo na camera {channel}')

    url = f"ws://localhost:8000/ws/results/{plugin_name}/{channel}?token={token}"
    ws = await websockets.connect(url)

    reader = FrameReader(channel)

    try:
        reader.start()
        while reader.isRunning():
            frame = reader.read()
            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            await send_image(ws, gray_image)
            await asyncio.sleep(1 / FPS)
    except Exception as e:
        print('Erro ao ler frames')
    finally:
        reader.close()
        await ws.close()


if __name__ == "__main__":
    plugin_name = sys.argv[1]
    channel = int(sys.argv[2])
    token = sys.argv[3]
    asyncio.run( main(plugin_name, channel, token) )