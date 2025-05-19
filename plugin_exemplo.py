from shared_frame_io import FrameReader
import cv2
import time
import sys

def main(camera_id):
    reader = FrameReader(camera_id)
    print(f'Rodando plugin exemplo na camera {camera_id}')
    try:
        reader.start()
        while reader.isRunning():
            frame = reader.read()
            cv2.imshow("Plugin Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            time.sleep(0.01)
    except Exception as e:
        print('Erro ao ler frames')
    finally:
        reader.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    camera_id = int(sys.argv[1])
    main(camera_id)