from shared_frame_io import FrameReader
import cv2
import time
import sys

def main(camera_id):
    reader = FrameReader(camera_id)
    print('RODANDO PLUGIN EXEMPLO')
    try:
        while True:
            frame = reader.read()
            cv2.imshow("Plugin Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            time.sleep(0.01)
    finally:
        reader.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    camera_id = int(sys.argv[1])
    main(camera_id)