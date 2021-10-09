from typing import Union
from app import ChatBox
import numpy as np
from nltk import word_tokenize
from os import environ

# Disabling warning/logging of Tensorflow.
environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
from nltk.stem.lancaster import LancasterStemmer
from tensorflow.keras.models import load_model
from random import choice
from re import compile
from pickle import load as pkload, dump as pkdump
from json import load as jload
from msgforms import (
    DefineFrame,
    NoteAddFrame,
    NoteShowFrame,
    TimeFrame,
    _BotFrameMsg,
    NameFrame,
)
from sqlite3 import connect
from pytz import country_timezones, country_names
from datetime import datetime
from requests import get, exceptions as req_except

INV_COMMA_SINGLE_re = compile(r"\s*'\s*")
IGN_LETTERS_re = compile(r"\?|!|\.|:|,|\(|\)|'")
PLACE_PREPOSITION = compile(r"\s(?:in|at|on)\s(?=\w+)")


class ChatBot:
    """
    This object represents the chat bot that will be integrated to the app.
    To get the response from chatbot we call `self.get_response` which
    takes in only one argument that is the user message in the string format
    and returns the chatbot response to that message. If the chatbot confidence
    was found low, it rather returns a failure message.
    """

    def __init__(self, chatbox: ChatBox) -> None:
        self.chatbox = chatbox
        self.model = load_model("data/TensorBot_v2.h5")
        self.words, self.classes = pkload(open("data/chatbot_dump_v2.pkl", "rb"))
        self.intents = jload(open("data/intents.json", "r"))
        self.funcs = ChatBotFunctions(self)
        self.context = None
        self._stemmer = LancasterStemmer()
        self._contra = {
            "ain't": "am are not",
            "aren't": "are am not",
            "can't": "cannot",
            "can't've": "cannot have",
            "'cause": "because",
            "could've": "could have",
            "couldn't": "could not",
            "couldn't've": "could not have",
            "didn't": "did not",
            "doesn't": "does not",
            "don't": "do not",
            "hadn't": "had not",
            "hadn't've": "had not have",
            "hasn't": "has not",
            "haven't": "have not",
            "he'd": "he had would",
            "he'd've": "he would have",
            "he'll": "he shall will",
            "he'll've": "he shall will have",
            "he's": "he has is",
            "how'd": "how did",
            "how'd'y": "how do you",
            "how'll": "how will",
            "how's": "how has is",
            "i'd": "I had would",
            "i'd've": "I would have",
            "i'll": "I shall will",
            "i'll've": "I shall will have",
            "i'm": "I am",
            "i've": "I have",
            "isn't": "is not",
            "it'd": "it had would",
            "it'd've": "it would have",
            "it'll": "it shall will",
            "it'll've": "it shall will have",
            "it's": "it is",
            "let's": "let us",
            "ma'am": "madam",
            "mayn't": "may not",
            "might've": "might have",
            "mightn't": "might not",
            "mightn't've": "might not have",
            "must've": "must have",
            "mustn't": "must not",
            "mustn't've": "must not have",
            "needn't": "need not",
            "needn't've": "need not have",
            "o'clock": "of the clock",
            "oughtn't": "ought not",
            "oughtn't've": "ought not have",
            "shan't": "shall not",
            "sha'n't": "shall not",
            "shan't've": "shall not have",
            "she'd": "she had would",
            "she'd've": "she would have",
            "she'll": "she shall will",
            "she'll've": "she shall will have",
            "she's": "she has is",
            "should've": "should have",
            "shouldn't": "should not",
            "shouldn't've": "should not have",
            "so've": "so have",
            "so's": "so as is",
            "that'd": "that would had",
            "that'd've": "that would have",
            "that's": "that has is",
            "there'd": "there had would",
            "there'd've": "there would have",
            "there's": "there has is",
            "they'd": "they had would",
            "they'd've": "they would have",
            "they'll": "they shall will",
            "they'll've": "they shall have will have",
            "they're": "they are",
            "they've": "they have",
            "to've": "to have",
            "wasn't": "was not",
            "we'd": "we had would",
            "we'd've": "we would have",
            "we'll": "we will",
            "we'll've": "we will have",
            "we're": "we are",
            "we've": "we have",
            "weren't": "were not",
            "what'll": "what shall will",
            "what'll've": "what shall will have",
            "what're": "what are",
            "what's": "what has is",
            "what've": "what have",
            "when's": "when has is",
            "when've": "when have",
            "where'd": "where did",
            "where's": "where has is",
            "where've": "where have",
            "who'll": "who shall will",
            "who'll've": "who shall will have",
            "who's": "who has is",
            "who've": "who have",
            "why's": "why has is",
            "why've": "why have",
            "will've": "will have",
            "won't": "will not",
            "won't've": "will not have",
            "would've": "would have",
            "wouldn't": "would not",
            "wouldn't've": "would not have",
            "y'all": "you all",
            "y'all'd": "you all would",
            "y'all'd've": "you all would have",
            "y'all're": "you all are",
            "y'all've": "you all have",
            "you'd": "you had would",
            "you'd've": "you would have",
            "you'll": "you shall will",
            "you'll've": "you shall will have",
            "you're": "you are",
            "you've": "you have",
            "wanna": "want to",
            " m ": " am ",
            " u ": " you ",
        }

    def _clean_text(self, sentence: str) -> str:
        """
        This method cleans the short forms used by the user in
        the message

        Args:
            sentence (str): The sentence user sends

        Returns:
            str: The cleaned sentence in lowercase.
        """
        sentence = sentence.lower()
        sentence = " " + INV_COMMA_SINGLE_re.sub("", sentence)
        for contra in self._contra:
            if contra in sentence:
                sentence.replace(contra, self._contra[contra])
                continue
            if "'" in contra:
                contra_ = contra.replace("'", "")
                if contra_ in sentence.split(" ") and contra not in self.words:
                    sentence.replace(contra_, self._contra[contra])
            sentence = IGN_LETTERS_re.sub("", sentence)
        return sentence[1:]

    def _bag_of_words(self, sentence: str) -> np.ndarray:
        """
        Extract the words and form the bag of word out of it.

        Args:
            sentence (str): The cleaned-sentence

        Returns:
            np.ndarray: Bag of words. Eg. [1,0,0,0,1,...n] where `n` is the count
            of words bot recognise
        """
        sentence_word = word_tokenize(sentence)
        sentence_word = [self._stemmer.stem(word) for word in sentence_word]
        bag = [0] * len(self.words)
        word_match_counter = 0
        for sent_word in sentence_word:
            for i, word in enumerate(self.words):
                if sent_word == word:
                    bag[i] = 1
                    word_match_counter += 1
        if word_match_counter != 0:
            return np.array([bag])
        else:
            return None

    def _predict_class(self, bag: np.ndarray) -> np.ndarray:
        """
        Predicts the class/intent of the bag passed

        Args:
            bag (np.ndarray): Bag of words

        Returns:
            np.ndarray: An array of recognised intents with there probability
        """
        results = self.model.predict(bag)[0]
        likely_classes = [
            (intent, res) for intent, res in zip(self.classes, results) if res > 0.1
        ]
        likely_classes.sort(key=lambda x: x[1], reverse=True)
        return np.array(likely_classes)

    def get_response(self, message: str) -> Union[str, _BotFrameMsg]:
        """
        Gets the response of a human message.

        Args:
            message (str): Text passed by user.

        Returns:
            Union[str, _BotFrameMsg]: A message in form of string or
            a Special form of `QFrame` that functions of what user need.
        """
        message = self._clean_text(message)
        bag = self._bag_of_words(message)
        if bag is not None:
            prob_intents = self._predict_class(bag)
            if len(prob_intents) > 3:
                return choice(
                    [
                        "Sorry didn't catch that",
                        "I didn't get that",
                        "I can not understand that sorry.",
                        "I- I.. m not sure what you mean.",
                    ]
                )
        else:
            return "I understand non of those beautiful words."
        _intents = []
        for _intent in self.intents:
            if _intent["intent"] in prob_intents:
                _intents.append(_intent)
        # If we have context set, than we need to be greedy towards
        # Contextual intents and run the intent which matches the context
        for _intent in _intents:
            if _intent.get("cont_get", None) == self.context:
                return self.process_intent(_intent, message)
        return self.process_intent(_intents[0], message)

    def process_intent(self, intent, message):
        """
        Sets the context, and returns the response according
        to the intent.
        """
        self.context = intent.get("cont_set", None)
        if "func" in intent.keys():
            return self.funcs.functions[intent["func"]](message)
        elif "responses" in intent.keys():
            resp = choice(intent["responses"])
            if isinstance(resp, list):
                self.context = resp[1]
                return resp[0]
            else:
                return resp
        else:
            return "Hmmm..."

    def close(self):
        # We must close the database connection.
        self.funcs.db.close()


class ChatBotFunctions:
    """
    This class holds all the chatbot functions that gets called when there
    corresponding intent is triggered by the user.
    """

    def __init__(self, chatbot: ChatBot) -> None:
        self.chatbot = chatbot
        self.db = connect("data/SideData.sqlite3")
        # I used this api for fetching jokes and definations.
        self._jokes_api_url = "https://v2.jokeapi.dev/joke/Programming,Miscellaneous,Dark,Spooky?blacklistFlags=nsfw"
        self._define_api_url = "https://api.dictionaryapi.dev/api/v2/entries/en/"
        try:
            self._user_name = pkload(open("data/username.pkl", "rb"))
        except FileNotFoundError:
            self._user_name = None
        self.functions = {
            "good_time": self._good_time,
            "make_joke": self._make_joke,
            "time_user": self._time_user,
            "time_somewhere": self._time_somewhere,
            "define": self._define,
            "add_to_do": None,
            "show_to_do": None,
            "create_a_note": self._create_note,
            "show_note": self._show_note,
            "mimic": None,
            "wish_birthday": None,
            "set_user_name": self._set_user_name,
            "get_user_name": self._get_user_name,
        }

    @property
    def user_name(self):
        return self._user_name or ""

    @user_name.setter
    def user_name(self, text: str):
        # Dump the user name string so that we can access it later,
        pkdump(text, open("data/username.pkl", "wb+"))
        self._user_name = text

    def _time_user(self, text: str):
        """
        This method first checks whether the user is
        asking for the time at some other place. If the check
        fails, it rather return a designed `QFrame` that shows
        the current time for the user.
        """
        if " in " in text or " at " in text or " on " in text:
            return self._time_somewhere(text)
        timeframe = TimeFrame(self.chatbot.chatbox)
        # Here we are not passing any parameter
        # So it will add the current time of the user.
        timeframe.add_time_from_timezone()
        timeframe.apply()
        return timeframe

    def _time_somewhere(self, text: str):
        """
        This function will search for the timezone in the database.
        if there is any match, it returns the time for that timezone.
        Matches for city and country gives the time for all the timezone
        that are connected to that country.
        """
        prob_place_name = PLACE_PREPOSITION.split(text)[-1]
        if prob_place_name.endswith(" now"):
            prob_place_name = " ".join(prob_place_name.split(" ")[:-1])
        curs = self.db.cursor()
        curs.execute(
            "SELECT country_code FROM timezones "
            f"WHERE country_code='{prob_place_name}' "
            f"OR country_name='{prob_place_name}';"
        )
        place_code = curs.fetchone()
        if place_code is None:
            curs.execute(
                "SELECT country_code FROM timezones "
                f"WHERE country_city LIKE '%{prob_place_name}%';",
            )
            place_code = curs.fetchone()
        if place_code is None:
            return self._time_user("place not found.")
        timezones = country_timezones[place_code[0]]
        timeFrame = TimeFrame(self.chatbot.chatbox, country_names[place_code[0]])
        for tz in timezones:
            timeFrame.add_time_from_timezone(tz)
        timeFrame.apply()
        return timeFrame

    def _good_time(self, text: str):
        """
        Greets the user according to the time.
        """
        time_now = datetime.now()
        greet_msg = choice(["A very great", "Good", "Very good", "Happy"])

        def hour_in_range(start, stop):
            return time_now.hour >= start and time_now.hour < stop

        if hour_in_range(6, 12):
            greet_msg += " morning"
        elif hour_in_range(12, 17):
            greet_msg += " afternoon"
        elif hour_in_range(17, 21):
            greet_msg += " evening"
        else:
            greet_msg += " night"
        greet_msg += ", " + self.user_name
        return greet_msg

    def _set_user_name(self, text: str):
        """
        Returns a `QFrame` that has a option to Set/Change the name.
        """
        nameFrame = NameFrame(self.chatbot.chatbox, self.user_name)

        def textChanged(text: str):
            if len(text) < 2 or text == self.user_name:
                nameFrame.saveBtn.setDisabled(True)
            else:
                nameFrame.saveBtn.setEnabled(True)

        nameFrame.nameEdit.textChanged.connect(textChanged)
        nameFrame.nameEdit.returnPressed.connect(nameFrame.saveBtn.click)

        def saveName():
            new_name = nameFrame.nameEdit.text()
            self.user_name = new_name

        nameFrame.saveBtn.clicked.connect(saveName)

        def cancelName():
            nameFrame.nameEdit.setDisabled(True)
            nameFrame.cancel.setDisabled(True)

        nameFrame.cancelBtn.clicked.connect(cancelName)
        nameFrame.apply()
        return nameFrame

    def _get_user_name(self, text: str):
        """
        This is called when user asks there own name.
        """
        if self.user_name:
            return choice(
                [
                    "Your name is {}",
                    "It's {}, you told me that.",
                    "It's {}, thats what I remember",
                    "Your name was set to {}.",
                    "It's {}",
                ]
            ).format(self.user_name.capitalize())
        else:
            return self._set_user_name(text)

    def _make_joke(self, text: str):
        """
        Makes an api call. If it fails to fetch the joke, this
        function returns a string that confirms that the api call
        was unseccessful.
        """
        try:
            response = get(self._jokes_api_url, timeout=3)
            response.raise_for_status()
            response: dict = response.json()
            if response["error"]:
                raise req_except.InvalidSchema
        except Exception:
            return "Sorry, I couldn't fetch a joke for you."
        if "joke" in response:
            return response["joke"]
        else:
            joke = (
                response["setup"]
                + f'<br \> {"".join(["―" for i in range(10)])} <br \>'
                + response["delivery"]
            )
            return joke

    def _define(self, text: str):
        word = self.__extract_word_to_define(text)
        frame = DefineFrame(self.chatbot.chatbox, word)
        try:
            response = get(self._define_api_url + word)
            response = response.json()
        except:
            frame.apply()
            return frame
        frame.set_response(response[0])
        frame.apply()
        return frame

    def __extract_word_to_define(self, text: str):
        words = text.split(" ")
        accept_next_word = False
        for i, word in enumerate(words):
            # First we need to check whether
            # the word is artical or not
            if word in ["the", "a", "an", "meaning", "word", "of", "defination"]:
                continue
            if word in ["define", "of", "is", "does", "by"]:
                accept_next_word = True
                continue
            if accept_next_word:
                return word
        return word

    def _show_note(self, text: str):
        curs = self.db.cursor()
        curs.execute("SELECT * FROM notes")

    def _create_note(self, text: str):
        frame = NoteAddFrame(self.chatbot.chatbox)
        frame.apply()

        def save_note_to_db():
            title = frame.titleEdit.text()
            desc = frame.descEdit.toPlainText()
            curs = self.db.cursor()
            curs.execute(
                "INSERT INTO notes VALUES (?, ?, ?);",
                [title, desc, datetime.now().timestamp()],
            )
            self.db.commit()
            curs.close()
            frame.createBtn.setText("Created")

        frame.createBtn.clicked.connect(save_note_to_db)
        return frame

    def _show_note(self, text: str) -> None:
        frame = NoteShowFrame(self.chatbot.chatbox)
        curs = self.db.cursor()
        curs.execute("SELECT * FROM notes")
        notes = curs.fetchall()
        curs.close()
        for note in notes:
            title = note[0]
            desc = (
                datetime.fromtimestamp(note[2]).strftime(
                    '%a %d %b, %Y <span style="color:32a852;">|</span> %H:%M'
                )
                + "<br>"
                + note[1]
            )
            frame.append_note(title, desc)

        def delete_note_from_db():
            curs = self.db.cursor()
            curs.execute(
                "DELETE FROM notes WHERE title = ?",
                (frame.notes[frame._now_showing][0],),
            )
            self.db.commit()
            curs.close()

        frame.del_btn.clicked.connect(delete_note_from_db)
        frame.apply()
        return frame
