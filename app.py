from tkinter import *
import time
from tkinter import filedialog
# from tkinter import messagebox

import numpy as np
import random as rand
from tensorflow import keras
import cv2

window_dim = "1150x850"
labels = ['anger','contempt','neutral','fear','happy','sadness','Neutral']
# labels = ['Neutral', 'Neutral', 'neutral', 'neutral', 'happy', 'neutral', 'neutral']
model = keras.models.load_model("data1.h")
modelEmo = keras.models.load_model("model_keras.h5")


def face(img_path):
    faceCascade = cv2.CascadeClassifier("face.xml")
    image = cv2.imread(img_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
    )
    cropped = []
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        crop_img = image[y:y + h, x:x + w]
        cropped.append(crop_img)
    cv2.imwrite("face.jpg", cropped[0])


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


def preprocess():
    image = cv2.imread("face.jpg", 0)
    image = cv2.resize(image, dsize=(64, 64))
    image = image.reshape((image.shape[0], image.shape[1], 1))
    image = image / 255
    return image


def preprocessEmo():
    image = cv2.imread("face.jpg")
    image = cv2.resize(image, (48, 48))
    image = np.array([image])
    image = image.astype('float32')
    image = image / 255
    return image


class ChatInterface(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.botname = 'Movie Recommender'
        self.entry_count = 0
        self.ml_features = []

        # sets default bg for top level windows
        self.tl_bg = "#EEEEEE"
        self.tl_bg2 = "#EEEEEE"
        self.tl_fg = "#000000"
        self.font = "Verdana 10"

        self.text_frame = Frame(self.master, bd=6)
        self.text_frame.pack(expand=True, fill=BOTH)

        # scrollbar for text box
        self.text_box_scrollbar = Scrollbar(self.text_frame, bd=0)
        self.text_box_scrollbar.pack(fill=Y, side=RIGHT)

        # contains messages
        self.text_box = Text(self.text_frame, yscrollcommand=self.text_box_scrollbar.set, state=DISABLED,
                             bd=1, padx=6, pady=6, spacing3=8, wrap=WORD, bg=None, font="Verdana 10", relief=GROOVE,
                             width=10, height=1)
        self.text_box.pack(expand=True, fill=BOTH)
        self.text_box_scrollbar.config(command=self.text_box.yview)

        self.text_box.configure(state=NORMAL)
        self.text_box.insert(END, self.botname + ' : Hi, May I know Your name?\n')

        # frame containing user entry field
        self.entry_frame = Frame(self.master, bd=1)
        self.entry_frame.pack(side=LEFT, fill=BOTH, expand=True)

        # entry field
        self.entry_field = Entry(self.entry_frame, bd=1, justify=LEFT)
        self.entry_field.pack(fill=X, padx=6, pady=6, ipady=3)
        # self.users_message = self.entry_field.get()

        # frame containing send button and emoji button
        self.send_button_frame = Frame(self.master, bd=0)
        self.send_button_frame.pack(fill=BOTH)

        # send button
        self.live_btn = Button(self.send_button_frame, text="Go Live", width=5, relief=GROOVE, bg='#263942',
                               bd=1, command=self.open_cam, activebackground="#263942")
        self.live_btn.pack(side=LEFT, ipady=8)
        # live button
        # self.quit_btn = Button(self.send_button_frame, text="Quit", width=5, relief=GROOVE, bg='white',
        #                        bd=1, command=self.on_closing(), activebackground="#FFFFFF",
        #                        activeforeground="#000000")
        # self.quit_btn.pack(side=LEFT, ipady=8)
        # quit button

        if self.entry_count < 0:

            self.send_button = Button(self.send_button_frame, text="Send", width=5, relief=GROOVE, bg='white',
                                      bd=1, command=lambda: self.send_message_insert_pause(None),
                                      activebackground="#FFFFFF",
                                      activeforeground="#000000")
            self.send_button.pack(side=LEFT, ipady=8)
            self.master.bind("<Return>", self.send_message_insert_pause)

        else:

            self.send_button = Button(self.send_button_frame, text="Send", width=5, relief=GROOVE, bg='white',
                                      bd=1, command=lambda: self.send_message_insert(None), activebackground="#FFFFFF",
                                      activeforeground="#000000")
            self.send_button.pack(side=LEFT, ipady=8)
            self.master.bind("<Return>", self.send_message_insert)

        self.last_sent_label(date="No messages sent.")

    def send_message_insert_pause(self, message):

        self.text_box.configure(state=NORMAL)
        self.text_box.insert(END, 'Your chat has been ended' + "\n")
        self.text_box.configure(state=DISABLED)
        self.text_box.see(END)

    def open_cam(self):
        cam = cv2.VideoCapture(0)
        while (True):
            _, frame = cam.read()
            frame = cv2.flip(frame, 1)
            # img = Image.fromarray(frame)
            suggestion = "test"
            if (cv2.waitKey(1) & 0xFF == ord("a")):
                img = cv2.imwrite("frame.jpg", frame)
                if (img != None):
                    image = face("frame.jpg")
                    imgAge = preprocess()
                    prediction = model.predict(np.array([imgAge]))
                    agePred = prediction[0][0]
                    gender = prediction[1][0]
                    imgEmo = preprocessEmo()
                    predictEmo = modelEmo.predict_classes([imgEmo])
                    emotion = labels[predictEmo[0]]
                    # print("Age=",get_age(agePred))
                    self.bot_text('Age=' + str(get_age(agePred)))
                    self.bot_text('Emo=' + str(emotion))
                    self.bot_text('Gender=' + str(get_gender(gender)))
                    break

            cv2.putText(frame, str(suggestion), (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.imshow("Tracking", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cam.release()
        cv2.destroyAllWindows()
        if agePred >= 0 and agePred < 18:

            if emotion == 'disgust':
                if gender == 'Male':
                    mov_list = ["'Casablanca'","'A beautiful Mind'","'The Matrix'",
                                            "'The Great Dictator'","'GreenZone'","'You can't be neutral on'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text()
                else:
                    mov_list = ["a2", "b2", "c2"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
            elif emotion == 'sad':
                if gender == 'Male':
                    mov_list = ["'Neerja'", "'Angrezi medium'", "'Head in the clouds '","'The Holiday'","'The Theory of Everything'","'Black'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Kung Fu Panda"')
                else:
                    mov_list = ["'Good Burger'","'Accepted'","'Feel the Beat'","'Love and Monsters'","'Dhamaal'","'Hera Pheri'","'Kung Fu Panda'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "The Little Mermaid."')
            elif emotion == 'happy':
                if gender == 'Male':
                    mov_list = ["'The fault in our stars'","'A walk to remember'","'Speak'","'Udaan'","'Tare zameen par'","'The Little Mermaid'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Cars"')
                else:
                    mov_list = ["'Harry potter and the Socrcere’s Stone'","'The Parent Trap'","'Back to the future'","'Back to the future'","'Freaky Friday'","'Andaz Apna Apna'","'Cars'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Finding Nemo"')
            else:
                if gender == 'Male':
                    mov_list = ["'The Jungle Book'","'Paradise'","'Aladdin'","'Good Will Hunting'","'Queen'","'Highway'","'Finding Nemo'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "The Lion King"')
                else:
                    mov_list = ["'Inside out'","'Inception '","'One flew over the cuckoo’s nest'","'Good will hunting '","'The sixth sense'","'Saaransh'","'Avengers'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Mulan"')



        elif agePred >= 19 and agePred < 30:
            # mov_list = dict()
            if emotion == 'neutral':
                if gender == 'Male':
                    mov_list = ["'Dear Zindagi'","'Yeh Jawani Hai Diwani'","'Frozen'","'Elf'","'Panga'","'Mary kom '","'Life of Pi'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Avengers"')
                else:

                    mov_list = ["'Clueless'","'Up!'","'Boy story'","'Andhadhun'","'It’s a wonderful life'","'Breakfast at fiffancy’s'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Yeh Jawani Hai Diwani."')
            elif emotion == 'sad':
                if gender == 'Male':
                    mov_list = ["'The Farewell'","'Pride and Prejudice'","'Romeo Juliet'","'Chhichhore'","'Lootera'","'Baghban'","'Anand'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Andhadhun"')
                else:
                    mov_list = ["'TED'","'There’s something about Mary'","'Blockers'","'Eurotrip'","'Knocked up'","'De Dana Dhan'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Chhichhore"')
            elif emotion == 'happy':
                if gender == 'Male':
                    mov_list = ["'Luka Chuppi'","'3 Idiots'","'Zindgi na Milegi Dobara'","'Clueless'","'Bring it on'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "De dana dhan"')
                else:
                    mov_list = ["'Lady Bird'","'The Joyluck Club'","'Piku'","'Chak de India'","'English Vinglish'","'Mardaani'","'Jo Jeeta Wohi Sikandar'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Luka Chuppi"')
            else:
                if gender == 'Male':
                    mov_list = ["'The notebook'","'Million Dollar Baby'","'Love in the Time of Cholera'","'Dostana'","'Paa'","'Buena Vista Social Club'","'Saaransh'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Bhaag Milkha Bhaag"')
                else:
                    mov_list = ["'Lakshya'","'Cocoon'","'Jaane bhi do yaara'","'Golmaal(1979)'","'About Schmidt'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Stree"')


        elif agePred >= 30 and agePred < 60:
            # mov_list = dict()
            if emotion == 'neutral':
                if gender == 'Male':
                    mov_list = ["'Baghban'","'Going the distance'","'Picture perfect'","'Begin again'","'How to be Single'","'Addicted to love'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Jo Jeeta Wohi Sikandar"')
                else:
                    mov_list = ["'Rocket Singh'","'Letters to Juliet'","'Get low'","'Harry Brown'","'Gran Torino'","'Happy Ending'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Saaransh"')
            elif emotion == 'sad':
                if gender == 'Male':
                    mov_list = ["'Dil Chahta Hai'","'Mamma Mia!'","'Four wedding and a Funeral'","'Matilda'","'One fine day '","'Mary poppins'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Lakshya "')
                else:
                    mov_list = ["'Harry Brown'","'Gran Torino'","'Gotta Dance'","Young at Heart'","'No Country for Old Men'","'Away from Her'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Baghban"')
            elif emotion == 'happy':
                if gender == 'Male':
                    mov_list = ["'The Queen'","'Sunset Boulevard'","'What Ever Happened To Baby Jane?'","'Philomena'","'English Vinglish'","'Irisi'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Rocket Singh"')
                else:
                    mov_list = ["'Letters to Juliet'","'Get Low'","'Mrs. Palfrey at the Claremont'","'Happy Tears'","'The Savages'","'Boynton Beach Club'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Dil Chahta Hai"')
            else:
                if gender == 'Male':
                    mov_list = ["'Divine Secrets Of The Ya-Ya Sisterhood'","'Grandma'","'Hello, My Name Is Doris'","'The Second Best Exotic Marigold Hotel'","'Florence Foster Jenkins'","'Senior Moment'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))
                # self.bot_text('You should watch "Lage Raho Munna Bhai"')
                else:
                    mov_list = ["'Lakshya'","'Cocoon'","'Jaane bhi do yaara'","'Golmaal(1979)'","'About Schmidt'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))

        elif agePred > 60:
            if emotion == 'neutral':
                if gender == 'Man':

                    mov_list = ["'Harry Brown'", "'Gran Torino'", "'Gotta Dance'", "Young at Heart'",
                                "'No Country for Old Men'", "'Away from Her'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))

                else:
                    mov_list = ["'The Queen'", "'Sunset Boulevard'", "'What Ever Happened To Baby Jane?'"
                        , "'Philomena'", "'English Vinglish'", "'Irisi'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))

            elif emotion == 'sad':
                if gender == 'Man':
                    mov_list = ["'Letters to Juliet'", "'Get Low'", "'Mrs. Palfrey at the Claremont'",
                                "'Happy Tears'", "'The Savages'", "'Boynton Beach Club'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))

                else:
                    mov_list = ["'Driving Miss Daisy'", "'Calendar Girls'", "'The Best Exotic Marigold Hotel'",
                                "'Arsenic And Old Lace'", "'The Lady In The Van'", "'Harold And Maude'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))

            elif emotion == 'happy':
                if gender == 'Man':

                    mov_list = ["'Letters to Juliet'", "'Get low'", "'Happy Tears'", "'Mrs. Palfrey at the Claremont'",
                                "'The Savages'", "'Boynton Beach Club'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))

                else:

                    mov_list = ["'Divine Secrets Of The Ya-Ya Sisterhood'", "'Grandma'", "'Hello, My Name Is Doris'",
                                "'The Second Best Exotic Marigold Hotel'", "'Florence Foster Jenkins'",
                                "'Senior Moment'"]
                    ch = rand.choice(mov_list)
                    self.bot_text('You should watch {}'.format(ch))


    def last_sent_label(self, date):
        try:
            self.sent_label.destroy()
        except AttributeError:
            pass

        self.sent_label = Label(self.entry_frame, font="Verdana 7", text=date, bg=self.tl_bg2, fg=self.tl_fg)
        self.sent_label.pack(side=LEFT, fill=X, padx=3)

    def bot_text(self, message):
        self.text_box.configure(state=NORMAL)
        self.text_box.insert(END, self.botname + " : " + message + "\n")
        self.text_box.configure(state=DISABLED)
        self.text_box.see(END)
        time.sleep(0)

    def user_text(self):
        self.text_box.configure(state=NORMAL)
        user_input = self.entry_field.get()
        self.text_box.insert(END, "You : " + user_input + "\n")
        self.text_box.configure(state=DISABLED)
        self.text_box.see(END)
        self.entry_field.delete(0, END)
        time.sleep(0)
        return user_input

    def open_files(self):
        self.file = filedialog.askopenfilename(initialdir="/", title="Select A File",
                                               filetypes=(("jpg files", "*.jpg"), ("png files", "*.png")))
        return self.file

    def send_message_insert(self, message):

        if self.entry_count == 0:
            user_input = self.user_text()

            self.bot_text(user_input + ", Kindly enter your image.")

            self.bot_text("Press Enter")

        elif self.entry_count == 1:
            self.image_path = self.open_files()
            print(self.image_path)
            self.bot_text("Please wait! Let me analyze it. :)")
            if self.image_path != ():
                image = face(self.image_path)
                imgAge = preprocess()
                prediction = model.predict(np.array([imgAge]))
                agePred = prediction[0][0]
                gender = prediction[1][0]
                imgEmo = preprocessEmo()
                predictEmo = modelEmo.predict_classes([imgEmo])
                emotion = labels[predictEmo[0]]
                # print("Age=",get_age(agePred))
                self.bot_text('Age=' + str(get_age(agePred)))
                self.bot_text('Emo=' + str(emotion))
                self.bot_text('Gender=' + str(get_gender(gender)))
                # print("Gender=",get_gender(gender))
                # print("Emo=",emotion)

                # if self.image_path != ():
                #     obj1 = DeepFace.analyze(img_path=self.image_path, actions=['age'])
                #     user_age = obj1["age"]
                #     self.bot_text('Predicted age is ' + str(user_age))
                #
                #     obj2 = DeepFace.analyze(img_path=self.image_path, actions=['gender'])
                #     user_gender = obj2["gender"]
                #     self.bot_text(str(user_gender))
                #
                #     obj3 = DeepFace.analyze(img_path=self.image_path, actions=['emotion'])
                #     user_emotion = obj3["dominant_emotion"]
                #     self.bot_text('Predicted emotion is ' + str(user_emotion))

                if agePred >= 0 and agePred < 18:

                    if emotion == 'disgust':
                        if gender == 'Male':
                            mov_list = ["'Casablanca'", "'A beautiful Mind'", "'The Matrix'",
                                        "'The Great Dictator'", "'GreenZone'", "'You can't be neutral on'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text()
                        else:
                            mov_list = ["a2", "b2", "c2"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                    elif emotion == 'sad':
                        if gender == 'Male':
                            mov_list = ["'Neerja'", "'Angrezi medium'", "'Head in the clouds '", "'The Holiday'",
                                        "'The Theory of Everything'", "'Black'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Kung Fu Panda"')
                        else:
                            mov_list = ["'Good Burger'", "'Accepted'", "'Feel the Beat'", "'Love and Monsters'",
                                        "'Dhamaal'", "'Hera Pheri'", "'Kung Fu Panda'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "The Little Mermaid."')
                    elif emotion == 'happy':
                        if gender == 'Male':
                            mov_list = ["'The fault in our stars'", "'A walk to remember'", "'Speak'", "'Udaan'",
                                        "'Tare zameen par'", "'The Little Mermaid'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Cars"')
                        else:
                            mov_list = ["'Harry potter and the Socrcere’s Stone'", "'The Parent Trap'",
                                        "'Back to the future'", "'Back to the future'", "'Freaky Friday'",
                                        "'Andaz Apna Apna'", "'Cars'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Finding Nemo"')
                    else:
                        if gender == 'Male':
                            mov_list = ["'The Jungle Book'", "'Paradise'", "'Aladdin'", "'Good Will Hunting'",
                                        "'Queen'", "'Highway'", "'Finding Nemo'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "The Lion King"')
                        else:
                            mov_list = ["'Inside out'", "'Inception '", "'One flew over the cuckoo’s nest'",
                                        "'Good will hunting '", "'The sixth sense'", "'Saaransh'", "'Avengers'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Mulan"')



                elif agePred >= 19 and agePred < 30:
                    # mov_list = dict()
                    if emotion == 'neutral':
                        if gender == 'Male':
                            mov_list = ["'Dear Zindagi'", "'Yeh Jawani Hai Diwani'", "'Frozen'", "'Elf'", "'Panga'",
                                        "'Mary kom '", "'Life of Pi'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Avengers"')
                        else:

                            mov_list = ["'Clueless'", "'Up!'", "'Boy story'", "'Andhadhun'", "'It’s a wonderful life'",
                                        "'Breakfast at fiffancy’s'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Yeh Jawani Hai Diwani."')
                    elif emotion == 'sad':
                        if gender == 'Male':
                            mov_list = ["'The Farewell'", "'Pride and Prejudice'", "'Romeo Juliet'", "'Chhichhore'",
                                        "'Lootera'", "'Baghban'", "'Anand'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Andhadhun"')
                        else:
                            mov_list = ["'TED'", "'There’s something about Mary'", "'Blockers'", "'Eurotrip'",
                                        "'Knocked up'", "'De Dana Dhan'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Chhichhore"')
                    elif emotion == 'happy':
                        if gender == 'Male':
                            mov_list = ["'Luka Chuppi'", "'3 Idiots'", "'Zindgi na Milegi Dobara'", "'Clueless'",
                                        "'Bring it on'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "De dana dhan"')
                        else:
                            mov_list = ["'Lady Bird'", "'The Joyluck Club'", "'Piku'", "'Chak de India'",
                                        "'English Vinglish'", "'Mardaani'", "'Jo Jeeta Wohi Sikandar'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Luka Chuppi"')
                    else:
                        if gender == 'Male':
                            mov_list = ["'The notebook'", "'Million Dollar Baby'", "'Love in the Time of Cholera'",
                                        "'Dostana'", "'Paa'", "'Buena Vista Social Club'", "'Saaransh'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Bhaag Milkha Bhaag"')
                        else:
                            mov_list = ["'Lakshya'", "'Cocoon'", "'Jaane bhi do yaara'", "'Golmaal(1979)'",
                                        "'About Schmidt'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Stree"')


                elif agePred >= 30 and agePred < 60:
                    # mov_list = dict()
                    if emotion == 'neutral':
                        if gender == 'Male':
                            mov_list = ["'Baghban'", "'Going the distance'", "'Picture perfect'", "'Begin again'",
                                        "'How to be Single'", "'Addicted to love'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Jo Jeeta Wohi Sikandar"')
                        else:
                            mov_list = ["'Rocket Singh'", "'Letters to Juliet'", "'Get low'", "'Harry Brown'",
                                        "'Gran Torino'", "'Happy Ending'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Saaransh"')
                    elif emotion == 'sad':
                        if gender == 'Male':
                            mov_list = ["'Dil Chahta Hai'", "'Mamma Mia!'", "'Four wedding and a Funeral'", "'Matilda'",
                                        "'One fine day '", "'Mary poppins'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Lakshya "')
                        else:
                            mov_list = ["'Harry Brown'", "'Gran Torino'", "'Gotta Dance'", "Young at Heart'",
                                        "'No Country for Old Men'", "'Away from Her'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Baghban"')
                    elif emotion == 'happy':
                        if gender == 'Male':
                            mov_list = ["'The Queen'", "'Sunset Boulevard'", "'What Ever Happened To Baby Jane?'",
                                        "'Philomena'", "'English Vinglish'", "'Irisi'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Rocket Singh"')
                        else:
                            mov_list = ["'Letters to Juliet'", "'Get Low'", "'Mrs. Palfrey at the Claremont'",
                                        "'Happy Tears'", "'The Savages'", "'Boynton Beach Club'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Dil Chahta Hai"')
                    else:
                        if gender == 'Male':
                            mov_list = ["'Divine Secrets Of The Ya-Ya Sisterhood'", "'Grandma'",
                                        "'Hello, My Name Is Doris'", "'The Second Best Exotic Marigold Hotel'",
                                        "'Florence Foster Jenkins'", "'Senior Moment'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))
                        # self.bot_text('You should watch "Lage Raho Munna Bhai"')
                        else:
                            mov_list = ["'Lakshya'", "'Cocoon'", "'Jaane bhi do yaara'", "'Golmaal(1979)'",
                                        "'About Schmidt'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))

                elif agePred > 60:
                    if emotion == 'neutral':
                        if gender == 'Man':

                            mov_list = ["'Harry Brown'", "'Gran Torino'", "'Gotta Dance'", "Young at Heart'",
                                        "'No Country for Old Men'", "'Away from Her'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))

                        else:
                            mov_list = ["'The Queen'", "'Sunset Boulevard'", "'What Ever Happened To Baby Jane?'"
                                , "'Philomena'", "'English Vinglish'", "'Irisi'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))

                    elif emotion == 'sad':
                        if gender == 'Man':
                            mov_list = ["'Letters to Juliet'", "'Get Low'", "'Mrs. Palfrey at the Claremont'",
                                        "'Happy Tears'", "'The Savages'", "'Boynton Beach Club'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))

                        else:
                            mov_list = ["'Driving Miss Daisy'", "'Calendar Girls'", "'The Best Exotic Marigold Hotel'",
                                        "'Arsenic And Old Lace'", "'The Lady In The Van'", "'Harold And Maude'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))

                    elif emotion == 'happy':
                        if gender == 'Man':

                            mov_list = ["'Letters to Juliet'", "'Get low'", "'Happy Tears'",
                                        "'Mrs. Palfrey at the Claremont'",
                                        "'The Savages'", "'Boynton Beach Club'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))

                        else:

                            mov_list = ["'Divine Secrets Of The Ya-Ya Sisterhood'", "'Grandma'",
                                        "'Hello, My Name Is Doris'",
                                        "'The Second Best Exotic Marigold Hotel'", "'Florence Foster Jenkins'",
                                        "'Senior Moment'"]
                            ch = rand.choice(mov_list)
                            self.bot_text('You should watch {}'.format(ch))

        self.last_sent_label(str(time.strftime("Last message sent: " + '%B %d, %Y' + ' at ' + '%I:%M %p')))
        self.entry_field.delete(0, END)
        # time.sleep(0)

        self.entry_count += 1

        print(self.entry_count)


splash_root = Tk()

# Adjust size
splash_root.geometry("1150x850")

# Set Label
canvas = Canvas(splash_root, width=1150, height=750)
canvas.pack()
img = PhotoImage(file="mrs4.png")
canvas.create_image(50, 50, anchor=NW, image=img)


def main():
    splash_root.destroy()
    gui = Tk()
    chatbot = ChatInterface(gui)
    gui.geometry(window_dim)
    gui.title("Movie Recommender")
    gui.iconbitmap('m.ico')


splash_root.after(3000, main)
mainloop()
# gui.mainloop()