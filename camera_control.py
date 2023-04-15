import cv2

cap = cv2.VideoCapture("rtsp://admin:alfaeta2022@192.168.9.103/media/video1")

while True:
    ret, image = cap.read()
    cv2.imshow("Test", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
