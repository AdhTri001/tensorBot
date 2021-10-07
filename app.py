from typing import Union, List
from PyQt5 import QtCore, QtGui, QtWidgets
from textwrap import wrap
from meta import res_rc  # Resources used by PyQt in icon and mic button
from speech_recognition import Microphone, Recognizer
from pickle import load as pkload


class MainWindow(QtWidgets.QMainWindow):
    "This class is the main window of Application."
    "This emits a signal while closing which helps me close the chatbot"

    closing = QtCore.pyqtSignal()

    @QtCore.pyqtSlot(QtGui.QCloseEvent)
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        """
        This event will fire the `closing` Signal. This helps close
        the worker threads if there are any.
        """
        self.closing.emit()
        return super().closeEvent(a0)


class TitleLabel(QtWidgets.QLabel):
    """
    This Class is a child of `QLabel` that when hovered over let the user drag the Window.
    This will be used in diplaying the title and the icon in the title-bar.
    """

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        # We get the root application from this method.
        def get_app(obj):
            if isinstance(obj, QtWidgets.QMainWindow):
                return obj
            else:
                return get_app(obj.parent())

        self.app: QtWidgets.QMainWindow = get_app(self)
        self.start: QtCore.QPoint = QtCore.QPoint(0, 0)
        self.pressed = False
        self.end: QtCore.QPoint = None

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.start = self.mapToGlobal(
            ev.pos()
        )  # Sets the starting point of draging of the window.
        self.pressed = True

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.pressed = False  # To stop window from following the mouse anymore.

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        if self.pressed:
            # If the mouse is pressed than we move the label.
            self.end = self.mapToGlobal(ev.pos())
            move = self.app.mapToGlobal(self.end - self.start)
            self.app.setGeometry(
                move.x(), move.y(), self.app.width(), self.app.height()
            )
            self.start = self.end

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        # At double click we will cycle the window to show maximized or normal.
        if self.app.isMaximized():
            self.app.showNormal()
        else:
            self.app.showMaximized()


class ChatBox(QtWidgets.QFrame):
    """
    This class holds the messages. Also have functions that take
    in message as string and add them in a vertical layout with a sweet
    pop-up animation. This class cache messages upto 25 messages.
    """

    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)

        # Here msgs and anims are just the cache list of message and animations.
        self.msgs: List[QtWidgets.QLabel] = []
        self.anims = []
        self.chatvertlay = QtWidgets.QVBoxLayout(self)
        self.msgfnt = QtGui.QFont()
        self.msgfnt.setPointSize(12)

    def append_msg(self, message):
        self.msgs.append(message)
        if len(self.msgs) > 30:
            # We remove the oldest message after 25 messages reached.
            msg = self.msgs.pop(0)
            msg.setParent(None)
            del msg

    @QtCore.pyqtSlot(str)
    def add_user_msg(self, text: str):
        """Adds the QLabel to the right side of the layout.

        Args:
            text (str): The text that will show up as user message.
        """
        text = text.strip()
        text = "\n".join(wrap(text, 80))
        message = QtWidgets.QLabel(text, self)
        message.setStyleSheet("border-top-right-radius:0px")
        self._add_msg_label(message, QtCore.Qt.AlignmentFlag.AlignRight)

    @QtCore.pyqtSlot(str)
    def add_bot_msg(self, text: str):
        """Adds the `QLabel` to the left side of the layout.
        Ther text on the label will be same as the text passed as arg

        Args:
            text (str): The text to set for QLabel
        """
        text = "\n".join(
            wrap(text, 80, break_long_words=False, replace_whitespace=False)
        )
        message = QtWidgets.QLabel(text, self)
        message.setStyleSheet("border-top-left-radius:0px")
        self._add_msg_label(message, QtCore.Qt.AlignmentFlag.AlignLeft)

    @QtCore.pyqtSlot(QtWidgets.QLabel, QtCore.Qt.AlignmentFlag)
    def _add_msg_label(self, message: QtWidgets.QLabel, align: QtCore.Qt.AlignmentFlag):
        # Setting up the label, calculating height and passing it for animation.
        message.setFont(self.msgfnt)
        message.setMaximumHeight(0)
        self.append_msg(message)
        final_height = message.text().count("\n") * 31 + 31
        self.chatvertlay.addWidget(message, 0, align)
        self._show_up_message(message, final_height)

    @QtCore.pyqtSlot(QtWidgets.QFrame)
    def add_bot_frame(self, frame: QtWidgets.QFrame):
        """
        Adds a QFrame(Container) as a bot's message.

        Args:
            frame (QtWidgets.QFrame): QFrame That will be added.
        """
        self.append_msg(frame)
        self.chatvertlay.addWidget(frame, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self._show_up_message(frame, frame._height)

    @QtCore.pyqtSlot(QtWidgets.QLabel, int)
    @QtCore.pyqtSlot(QtWidgets.QFrame, int)
    def _show_up_message(
        self, message: Union[QtWidgets.QLabel, QtWidgets.QFrame], fin_height: int
    ):
        anim = QtCore.QPropertyAnimation(message, b"maximumHeight")
        # C++ doesn't have any garbage collector, so we need to cahce it in our class attr.
        self.anims.append(anim)
        anim.setDuration(fin_height * 3)
        anim.setStartValue(0)
        anim.setEndValue(fin_height)
        # Remove the animation form list when finished.
        anim.finished.connect(lambda: self.anims.remove(anim))
        anim.start()


class App:
    """
    This is the main app class. Here we have all the objects that show up in the window as class attr.
    This class First creat the cache of widgets in `__init__` and then `setupUi` puts the objects in the right place
    with right values. Then it calls `retranslateUi` which translate the text gonna display in the title. Then we call
    `add_ui_logic` which adds the logic to cross button, minimize button, line box(Text box) and mic button.
    """

    def __init__(self, app: MainWindow):
        self.app = app
        # Central Widget that holds all other widgets
        self.centralwidget = QtWidgets.QWidget(self.app)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        # Title Bar Widgets
        self.titlebar = QtWidgets.QFrame(self.centralwidget)
        self.title_horzlay = QtWidgets.QHBoxLayout(self.titlebar)
        self.icon = TitleLabel(self.titlebar)
        self.title = TitleLabel(self.titlebar)
        self.minim = QtWidgets.QPushButton(self.titlebar)  # Minimize button
        self.cross = QtWidgets.QPushButton(self.titlebar)  # Maximized button
        # The Ares where chat shows up
        self.chatscroll = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollAreaContents = QtWidgets.QWidget()
        self.scrollHorzLay = QtWidgets.QHBoxLayout(self.scrollAreaContents)
        self.chatbox = ChatBox(self.scrollAreaContents)
        self.chatvertlay = self.chatbox.chatvertlay
        # Chat Staging Area. Here is the Mic button
        self.chatstage = QtWidgets.QFrame(self.centralwidget)
        self.chatstage_horzlay = QtWidgets.QHBoxLayout(self.chatstage)
        self.msgedit = QtWidgets.QLineEdit(self.chatstage)
        self.micbut = QtWidgets.QPushButton(self.chatstage)
        self.size_grip = QtWidgets.QSizeGrip(self.chatstage)
        self.speech_recog = Recognizer()
        # For Concurrency
        self.cb_worker = None
        self.cb_thread = None
        self.recog_worker = None
        self.recog_thread = None

    def setupUi(self):
        self.app.setObjectName("app")
        self.app.resize(1280, 640)  # Init size
        self.app.setMinimumSize(
            QtCore.QSize(1080, 540)
        )  # This is not required tho but just in case.
        # To allow curve edges.
        self.app.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.app.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.app.setStyleSheet("background:transparent;")
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout.setContentsMargins(0, 0, 0, 10)
        self.verticalLayout.setSpacing(
            0
        )  # We need title bar, chatbox, and chatstage to stick together.
        self.verticalLayout.setObjectName("verticalLayout")
        # Size Policy tells the object how it should Occupy the provided space.
        self.titlebar.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
            )
        )
        self.titlebar.setFixedHeight(30)
        self.titlebar.setStyleSheet(
            "background-color: rgb(18, 18, 18);\n"
            "color: rgb(255, 238, 238);\n"  # Pure white looks bad.
            "border-top-left-radius:20px;border-top-right-radius:20px;border-color:rgba(255, 255, 255, 0);"
        )
        self.titlebar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.titlebar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.titlebar.setObjectName("titlebar")
        self.title_horzlay.setContentsMargins(0, 0, 0, 0)
        self.title_horzlay.setSpacing(0)
        self.title_horzlay.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(
            40, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum
        )
        self.title_horzlay.addItem(spacerItem)
        self.icon.setAttribute(
            QtCore.Qt.WA_StyledBackground
        )  # For allowing StyleSheets to take power
        self.icon.setFixedSize(QtCore.QSize(30, 30))
        self.icon.setCursor(QtGui.QCursor(QtCore.Qt.SizeAllCursor))
        self.icon.setStyleSheet("border-radius:0px;")
        # Below `:/tensor` belongs to the resource py file we imported at the top. see line-4
        # The images that show up on my GUI are all made by me in blender which is an Open source program.
        # So no copyright issues :)
        self.icon.setPixmap(QtGui.QPixmap(":/tensor/meta/tensor(nonglow).png"))
        self.icon.setScaledContents(True)
        self.icon.setObjectName("icon")
        self.title_horzlay.addWidget(self.icon)
        self.title.setAttribute(
            QtCore.Qt.WA_StyledBackground
        )  # For allowing StyleSheets to take control again..
        font = self.title.font()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setCursor(QtGui.QCursor(QtCore.Qt.SizeAllCursor))
        self.title.setStyleSheet("border-radius:0px;")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setIndent(0)
        self.title.setObjectName("title")
        self.title_horzlay.addWidget(self.title)
        self.minim.setFixedSize(QtCore.QSize(61, 31))
        self.minim.setFont(font)
        self.minim.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.minim.setStyleSheet(
            "QPushButton#minim {border-radius:0}\n"
            "QPushButton#minim:hover {background-color:rgb(71, 71, 71);}\n"
            "QPushButton#minim:pressed {padding-left:2;padding-top:2;}"
        )
        self.minim.setObjectName("minim")
        self.title_horzlay.addWidget(self.minim)
        self.cross.setFixedSize(QtCore.QSize(61, 31))
        self.cross.setFont(font)
        self.cross.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.cross.setStyleSheet(
            "QPushButton#cross {border-top-left-radius:0}\n"
            "QPushButton#cross:hover {background-color: rgb(255, 74, 77);}\n"
            "QPushButton#cross:pressed {padding-left:2;padding-top:2;}"
        )
        self.cross.setObjectName("cross")
        self.title_horzlay.addWidget(self.cross)
        self.verticalLayout.addWidget(self.titlebar)
        self.chatscroll.setStyleSheet("background-color: rgb(33, 33, 33);border:0;")
        self.chatscroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.chatscroll.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.chatscroll.setWidgetResizable(True)
        self.chatscroll.setObjectName("chatscroll")
        self.scrollAreaContents.setGeometry(QtCore.QRect(0, 0, 1280, 500))
        # Same reason as mentioned above
        self.scrollAreaContents.setStyleSheet(
            "QLabel {border:1px solid rgb(0, 132, 255);border-radius:10px;background-color:rgb(48,48,48)}\n"
            "QGroupBox {border:2px solid qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(85, 255, 0, 255), stop:1 rgba(0, 132, 255, 255));border-bottom-right-radius:10px;border-bottom-left-radius:10px;border-top-right-radius:10px}"
        )
        self.scrollAreaContents.setObjectName("scrollAreaContents")
        self.scrollHorzLay.setContentsMargins(-1, 0, -1, -1)
        self.scrollHorzLay.setObjectName("scrollHorzLay")
        self.chatbox.setAttribute(
            QtCore.Qt.WA_StyledBackground
        )  # For allowing StyleSheets to take power
        self.chatbox.setStyleSheet("color:#eee;\n")
        self.chatbox.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.chatbox.setObjectName("chatbox")
        self.chatvertlay.setObjectName("chatvertlay")
        self.scrollHorzLay.addWidget(self.chatbox, 0, QtCore.Qt.AlignBottom)
        self.chatscroll.setWidget(self.scrollAreaContents)
        self.verticalLayout.addWidget(self.chatscroll)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chatstage.sizePolicy().hasHeightForWidth())
        self.chatstage.setSizePolicy(sizePolicy)
        self.chatstage.setFixedHeight(90)
        self.chatstage.setStyleSheet(
            "QFrame#chatstage {border-bottom-left-radius:20px;border-bottom-right-radius:20px;border-color:rgba(255, 255, 255, 0);background-color: rgb(33, 33, 33);}"
        )
        self.chatstage.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.chatstage.setFrameShadow(QtWidgets.QFrame.Raised)
        self.chatstage.setObjectName("chatstage")
        self.chatstage_horzlay.setObjectName("chatstage_horzlay")
        self.msgedit.setMinimumSize(QtCore.QSize(0, 60))
        font = self.msgedit.font()
        font.setPointSize(12)
        self.msgedit.setFont(font)
        self.msgedit.setStyleSheet(
            "QLineEdit#msgedit {background-color: rgb(72, 72, 72);border-radius:20px;border: 2px solid qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(85, 255, 0, 255), stop:1 rgba(0, 132, 255, 255));padding:7px;padding-left:10px;color:rgb(255,255,255);}"
        )
        self.msgedit.setObjectName("msgedit")
        self.chatstage_horzlay.addWidget(self.msgedit)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHeightForWidth(self.micbut.sizePolicy().hasHeightForWidth())
        self.micbut.setSizePolicy(sizePolicy)
        mic_icon = QtGui.QIcon()
        mic_icon.addPixmap(QtGui.QPixmap(":/tensor/meta/rnd_tens(nonglow).png"))
        mic_icon.addPixmap(
            QtGui.QPixmap(":/tensor/meta/rnd_ten(glow).png"), QtGui.QIcon.Disabled
        )
        self.micbut.animateClick(100)
        self.micbut.setIcon(mic_icon)
        self.micbut.setFixedSize(QtCore.QSize(60, 60))
        self.micbut.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.micbut.setStyleSheet(
            "QPushButton#micbut {border:0;}\n"
            "QPushButton#micbut:hover {padding-top:-2}\n"
            "QPushButton#micbut:pressed {padding-top:2}"
        )
        self.micbut.setText("")
        self.micbut.setIconSize(QtCore.QSize(60, 60))
        self.micbut.setObjectName("micbut")
        self.chatstage_horzlay.addWidget(self.micbut)
        self.verticalLayout.addWidget(self.chatstage)
        # For resizing the window.
        self.size_grip.setFixedSize(QtCore.QSize(10, 10))
        self.size_grip.setStyleSheet(
            "QSizeGrip {background-color:rgb(18,18,18);border:0}\n"
            "QSizeGrip:hover {border:1 solid rgba(0, 132, 255, 255)}"
        )
        self.chatstage_horzlay.addWidget(
            self.size_grip,
            0,
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignBottom,
        )
        self.app.setCentralWidget(self.centralwidget)

        self.retranslateUi(self.app)
        return self

    def retranslateUi(self, app):
        _trans = QtCore.QCoreApplication.translate
        self.title.setText(_trans("app", "Tensor Bot"))
        self.minim.setText("—")
        self.cross.setText("×")
        self.msgedit.setPlaceholderText(_trans("app", "Type your text here."))
        self.micbut.setShortcut(_trans("app", "Ctrl+Shift+A"))

    def add_ui_logic(self):
        self.cross.clicked.connect(self.app.close)
        self.minim.clicked.connect(self.app.showMinimized)
        self.chatscroll.verticalScrollBar().rangeChanged.connect(
            lambda min, max: self.chatscroll.verticalScrollBar().setSliderPosition(max)
        )

        def do_send():
            msg = self.msgedit.text()
            if (msg.__len__() > 500) or (msg.__len__() == 0):
                global WARNED
                if not WARNED:
                    self.chatbox.add_bot_msg(
                        "You can only send messages upto 500 character"
                        "and message can't be empty."
                    )
                WARNED = True
                return
            self.msgedit.setText("")
            self.msgedit.setDisabled(True)
            self.chatbox.add_user_msg(msg)
            run_chatbot(msg)

        def run_chatbot(msg):
            self.cb_worker = Chatbot_Worker()
            self.cb_thread = QtCore.QThread()
            self.cb_worker.moveToThread(self.cb_thread)
            self.cb_thread.started.connect(lambda: self.cb_worker.run(msg, CHATBOT))
            self.cb_worker.finished.connect(self.cb_thread.quit)
            self.cb_worker.finished.connect(self.cb_worker.deleteLater)
            self.cb_thread.finished.connect(re_enable_stage)
            self.cb_thread.finished.connect(self.cb_thread.deleteLater)
            self.cb_thread.start()

        def re_enable_stage():
            self.msgedit.setDisabled(False)
            self.msgedit.setFocus()

        self.msgedit.returnPressed.connect(do_send)
        self.micbut.setShortcut(QtGui.QKeySequence("Ctrl+Shift+A"))

        def recognise():
            self.recog_worker = SpeechRecog_Worker()
            self.recog_thread = QtCore.QThread()
            self.recog_worker.moveToThread(self.recog_thread)
            self.recog_worker.finished.connect(lambda: self.micbut.setEnabled(True))
            self.recog_worker.recognized.connect(
                lambda text: (
                    self.msgedit.setText(text),
                    self.msgedit.returnPressed.emit(),
                )
            )
            self.recog_thread.started.connect(self.recog_worker.run)
            self.recog_worker.finished.connect(self.recog_thread.quit)
            self.recog_worker.finished.connect(self.recog_worker.deleteLater)
            self.recog_thread.finished.connect(self.recog_thread.deleteLater)
            self.recog_thread.start()
            self.micbut.setDisabled(True)

        self.micbut.pressed.connect(recognise)

        def terminate_threads():
            try:
                self.cb_thread.terminate()
                self.recog_thread.terminate()
            except:
                pass

        self.app.closing.connect(terminate_threads)
        self.app.closing.connect(CHATBOT.close)


class Chatbot_Worker(QtCore.QObject):
    """
    This is a worker object that is processed in worder threads
    to run the chatbot and get the response.
    """

    finished = QtCore.pyqtSignal()

    def run(self, msg: str, chatbot):
        resp = chatbot.get_response(msg)
        if isinstance(resp, QtWidgets.QFrame):
            chatbot.chatbox.add_bot_frame(resp)
        else:
            chatbot.chatbox.add_bot_msg(resp)
        self.finished.emit()


class SpeechRecog_Worker(QtCore.QObject):
    """
    This is a worker object that is involved in speech recognisation.
    This also runs not on main thread because we don't want it to freeze our ui.
    """

    finished = QtCore.pyqtSignal()
    recognized = QtCore.pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.recogniser = Recognizer()

    def run(self):
        try:
            with Microphone() as mic:
                self.recogniser.adjust_for_ambient_noise(mic, duration=0.2)
                aud = self.recogniser.listen(mic)
                text = self.recogniser.recognize_azure(aud, API_KEY, location=API_LOC)
                assert text != "", "Couldn't recognize that"
        except Exception as err:
            print(repr(err))
            self.finished.emit()
            return
        self.recognized.emit(text)
        self.finished.emit()


if __name__ == "__main__":
    import sys
    from chatbot import ChatBot

    WARNED = False
    API_KEY, API_LOC = pkload(open("data/API.pkl", "rb"))
    app = QtWidgets.QApplication(sys.argv)
    # Adding The style sheet for QScrollBar Object because of CSS Parent issue.
    # Simply if I will add it in Scroll Area it won't effect the Scrollbar of the area.
    app.setStyleSheet(
        "QScrollBar:vertical {border:none;background:rgb(45, 45, 68);width:14px;margin:10px 0 10px 0;}\n"
        "QScrollBar::handle:vertical {background-color: rgb(80, 80, 122);min-height: 20px;border-radius: 7px;}\n"
        "QScrollBar::handle:vertical:hover{background-color: rgb(32, 214, 255);}\n"
        "QScrollBar::handle:vertical:pressed {background-color: rgb(0, 132, 255);}\n"
        "QScrollBar::sub-line:vertical {border: none;background-color: rgb(59, 59, 90);height: 10px;subcontrol-position: top;subcontrol-origin: margin;}\n"
        "QScrollBar::sub-line:vertical:hover {background-color: rgb(32, 214, 255);}\n"
        "QScrollBar::sub-line:vertical:pressed {background-color: rgb(0, 132, 255);}\n"
        "QScrollBar::add-line:vertical {border: none;background-color: rgb(59, 59, 90);height: 10px;subcontrol-position: bottom;subcontrol-origin: margin;}\n"
        "QScrollBar::add-line:vertical:hover {background-color: rgb(32, 214, 255);}\n"
        "QScrollBar::add-line:vertical:pressed {background-color: rgb(0, 132, 255);}\n"
        "QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {background: none;}\n"
        "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {background: none;}\n"
    )
    root = MainWindow()
    root.setWindowIcon(QtGui.QIcon("meta/icon.ico"))
    main_app = App(root)
    # Making CHATBOT variable global to not block main thread while getting response
    CHATBOT = ChatBot(main_app.chatbox)
    main_app.setupUi().add_ui_logic()
    root.show()
    root.raise_()
    root.activateWindow()
    sys.exit(app.exec_())
