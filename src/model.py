from keras.models import load_model  
import cv2 
import numpy as np
from pyautogui import move, click 

np.set_printoptions(suppress=True)

model = load_model("model/keras_Model.h5", compile=False)
class_names = [i.strip() for i in open("model/labels.txt", "r")]

def trackFace(image, pixels):
    image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
    image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
    image = (image / 127.5) - 1

    prediction = model.predict(image)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]

    print("Class:", class_name[2:])
    print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

    if int(str(np.round(confidence_score * 100))[:-2]) >= 80:
        match class_name[2:]:
            case "Left":
                move(-pixels, 0)
            case "Right":
                move(pixels, 0)
            case "Up":
                move(0, -pixels)
            case "Down":
                move(0, pixels)
            case "Left Click":
                click(button="left")
            case "Right Click":
                click(button="right")

if __name__ == "__main__":
    camera = cv2.VideoCapture(0)
    while True:
        ret, image = camera.read()

        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

        # Show the image in a window
        cv2.imshow("Webcam Image", image)

        trackFace(image)

        # Listen to the keyboard for presses.
        keyboard_input = cv2.waitKey(1)

        # 27 is the ASCII for the esc key on your keyboard.
        if keyboard_input == 27:
            break

    camera.release()
    cv2.destroyAllWindows()
