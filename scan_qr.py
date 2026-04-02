import cv2
from pyzbar.pyzbar import decode

def scan_qr():
    cap = cv2.VideoCapture(0)

    while True:
        _, frame = cap.read()

        for barcode in decode(frame):
            data = barcode.data.decode('utf-8')

            cap.release()
            cv2.destroyAllWindows()
            return data

        cv2.imshow('Scan QR (Press Q to exit)', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None