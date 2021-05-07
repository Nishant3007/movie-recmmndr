import cv2
import numpy as np
from tensorflow import keras

modelEmo = keras.models.load_model("model_keras.h5")
labels = ['anger','contempt','disgust','fear','happy','sadness','surprise']
image = cv2.imread("model.jpg")
image = cv2.resize(image,(48,48))
image = np.array([image])
image = image.astype('float32')
image = image/255
prediction = modelEmo.predict_classes([image])
print(labels[prediction[0]])


# cam = cv2.VideoCapture(0)
# while True:
#     _,frame = cam.read()
#     frame =cv2.flip(frame,1)
#     cv2.rectangle(frame, (620 - 1, 9), (1020 + 1, 419), (555, 0, 0), 1)
#     roi = frame[10:410, 620:920]
#     # gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
#     image = cv2.resize(roi, (48, 48))
#     image = np.array([image])
#     image = image.astype('float32')
#     image = image / 255
#     prediction = model.predict_classes([image])
#     print(labels[prediction[0]])
#
#     # prediction = model.predict(np.array([image]))
#     # age = get_age(prediction[0])
#     # gender = get_gender(prediction[1])
#     if prediction != None:
#         cv2.putText(frame, str(labels[prediction[0]]), (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 2)
#     # cv2.putText(frame, str(gender), (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 2)
#     cv2.imshow("Tracking", frame)
#
#     if cv2.waitKey(1) & 0xFF == ord("q"):
#         break
# cam.release()
# cv2.destroyAllWindows()