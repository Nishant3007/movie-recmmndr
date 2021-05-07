import cv2
import numpy as np
from tensorflow import keras
from PIL import Image

model=keras.models.load_model("data1.h")



def get_age(distr):
    distr = distr * 4
    if distr >= 0.65 and distr <= 1.4: return "0-18"
    if distr >= 1.65 and distr <= 2.4: return "19-30"
    if distr >= 2.65 and distr <= 3.4: return "31-60"
    if distr >= 3.65 and distr <= 4.4: return "60 +"
    return "Unknown"


def get_gender(prob):
    if prob < 0.5:
        return "Male"
    else:
        return "Female"


# print("predicted gender=",gender,"predicted age",age)

cam = cv2.VideoCapture(0)
while True:
    _,frame = cam.read()
    frame =cv2.flip(frame,1)
    cv2.rectangle(frame, (620 - 1, 9), (1020 + 1, 419), (555, 0, 0), 1)
    roi = frame[10:410, 620:920]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    image = roi

    prediction = model.predict(np.array([image]))
    age = get_age(prediction[0])
    gender = get_gender(prediction[1])
    cv2.putText(frame, str(age), (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 2)
    cv2.putText(frame, str(gender), (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 2)
    cv2.imshow("Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cam.release()
cv2.destroyAllWindows()