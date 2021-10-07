from PyQt5 import QtWidgets, QtGui, QtCore
from app import ChatBox
from pytz import timezone
from datetime import datetime, timezone as dt_tz

# I will add the stylesheet according to the widgets contained.
BTN_StyleSheet = "QPushButton {border:2 solid rgb(25, 155, 255);border-radius:5}\n"
LBL_StyleSheet = (
    "QLabel {border:0;border-bottom: 1 solid rgb(25, 155, 255);border-radius:0}\n"
)
LNE_StyleSheet = (
    "QLineEdit, QTextEdit {border:0;border-bottom: 1 solid rgb(25, 155, 255);border-radius:0;"
    "border-top-left-radius:10;border-top-right-radius:10}\n"
    "QLineEdit:disabled, QTextEdit:disabled {border-color: rgb(175, 5, 15);}\n"
)
SAVE_StyleSheet = (
    "QPushButton:hover {background-color: rgb(5, 75, 105);}\n"
    "QPushButton:disabled {border-color: rgb(90, 0, 5);}\n"
)
CANC_StyleSheet = "QPushButton:hover {background-color: rgb(90, 0, 5);}\n"
DEFINE_Style = (
    "<style>"
    " .pos{color: rgb(25, 155, 255);}"
    " .def{color: white;border-left:1px solid rgb(25, 155, 255);}"
    " .ex{color: rgb(190,190,190);font-size:18px;font-style:italic;margin-left:15px;}"
    "</style>\n"
)


class _BotFrameMsg(QtWidgets.QFrame):
    """
    This object is a abstract representation of bot's
    message that is sent in as a `QFrame` object.

    Inherits:
        QFrame
    """

    @QtCore.pyqtSlot(ChatBox)
    def __init__(self, parent: ChatBox) -> None:
        super().__init__(parent=parent)
        # First me set the style sheet for the contained QLabels.
        self.setStyleSheet(
            "QFrame {border:1px solid qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(85, 255, 0, 255), stop:1 rgba(0, 132, 255, 255));border-radius:15px;background-color:rgb(48,48,48)}"
            + LBL_StyleSheet
            + 'QLabel[accessibleName="heading"] {border-bottom-width: 3;}\n'  # Makes the border of QLabel thicker
        )
        self.setMinimumWidth(400)
        self.setMaximumWidth(800)
        self.vertlay = QtWidgets.QVBoxLayout(self)
        self.vertlay.setContentsMargins(10, 10, 10, 10)
        self.vertlay.setSpacing(0)
        self._heading = QtWidgets.QLabel(self)
        self._heading.setAccessibleName("heading")
        self._height = 35  # This is the approx height of the heading.

    @QtCore.pyqtSlot(str)
    def set_heading(self, text: str):
        fnt = QtGui.QFont()
        fnt.setPointSize(15)
        fnt.setBold(True)
        fnt.setWeight(75)
        self._heading.setFont(fnt)
        self._heading.setText(text)
        self._heading.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self._heading.setIndent(0)
        self.vertlay.addWidget(self._heading)

    def apply(self):
        """To be implemented in child classes."""


class TimeFrame(_BotFrameMsg):
    """
    This object will be added to chatbox which will display time
    for the provided timezones in a pretty grid.

    Inherits:
        _BotFrameMsg
    """

    @QtCore.pyqtSlot(ChatBox, str)
    def __init__(self, parent: ChatBox, place_name: str = None) -> None:
        super().__init__(parent)
        place_name = place_name or "Your place"
        self.set_heading(f"Current time in {place_name.capitalize()}")
        self.setStyleSheet(self.styleSheet())
        self.timezonesgrid = QtWidgets.QGridLayout()
        self.timezonesgrid.setContentsMargins(0, 0, 0, 0)
        self.timezonesgrid.setHorizontalSpacing(0)
        self.timezonesgrid.setVerticalSpacing(10)
        self.timelabels = []
        self.timefnt = QtGui.QFont()
        self.timefnt.setFamily("OCR A Extended")
        self.timefnt.setPointSize(15)
        self.timefnt.setBold(False)
        self.timefnt.setWeight(50)

    @QtCore.pyqtSlot(str)
    def add_time_from_timezone(self, tz=None):
        """
        Adds time-zone current time to be displayed in a
        QLabel. These Labels are styled by base class style sheet.
        """
        time = (
            datetime.now(timezone(tz))
            if tz is not None
            else datetime.now(dt_tz.utc).astimezone()
        )
        tz_name = QtWidgets.QLabel(self)
        fnt = tz_name.font()
        fnt.setPointSize(10)
        tz_name.setFont(fnt)
        tz_name.setText(tz if tz is not None else time.tzname())
        tz_name.setIndent(0)
        tz_name.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        tz_time = QtWidgets.QLabel(self)
        tz_time.setFont(self.timefnt)
        tz_time.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        tz_time.setText(
            time.strftime(
                '%I:%M %p<br/><span style="font-size:10pt;'
                'font-weight:600;color:#00a69b;">%d/%m/%Y</span>'
            )
        )
        self.timelabels.append((tz_name, tz_time))

    def apply(self):
        """
        After supplying all the timezones, we need to add them to
        the grid layout, which is done but this apply method.
        """
        i = 0
        for tz_name, tz_time in self.timelabels:
            self.timezonesgrid.addWidget(tz_name, i, 0, 1, 1)
            self.timezonesgrid.addWidget(tz_time, i, 1, 1, 1)
            self._height += 60
            i += 1
        self.vertlay.addLayout(self.timezonesgrid)


class NameFrame(_BotFrameMsg):
    """
    This frame helps user set there name with a QLineEdit.

    Inherits:
        _BotFrameMsg
    """

    @QtCore.pyqtSlot(ChatBox, str)
    def __init__(self, parent: ChatBox, name: str = None) -> None:
        super().__init__(parent)
        self.name = name
        self.nameEdit = QtWidgets.QLineEdit(self)
        self.btn_horzlay = QtWidgets.QHBoxLayout()
        self.saveBtn = QtWidgets.QPushButton("Save", self)
        self.cancelBtn = QtWidgets.QPushButton("Cancel", self)
        self._height += 140  # I measured myself, found this to be pretty accurate.
        self.setStyleSheet(self.styleSheet() + BTN_StyleSheet + LNE_StyleSheet)

    def apply(self):
        self.set_heading("Let me know your name")
        self.setFixedWidth(600)
        self.setObjectName("nameFrame")
        self.vertlay.setSpacing(30)
        self.set_heading("Let me know your name.")
        self.nameEdit.setText(self.name) if self.name is not None else None
        self.nameEdit.setMinimumHeight(40)
        self.nameEdit.setMaxLength(50)
        font = self.nameEdit.font()
        font.setPointSize(12)
        self.nameEdit.setFont(font)
        self.nameEdit.setPlaceholderText("Type your name.")
        self.nameEdit.setObjectName("nameEdit")
        self.vertlay.addWidget(self.nameEdit)
        self.btn_horzlay.setObjectName("btn_horzlay")
        self.saveBtn.setMinimumSize(QtCore.QSize(60, 30))
        self.saveBtn.setStyleSheet(SAVE_StyleSheet)
        self.saveBtn.setObjectName("save")
        self.saveBtn.setAccessibleName("save")
        self.saveBtn.setDisabled(True)
        self.btn_horzlay.addWidget(self.saveBtn, 0, QtCore.Qt.AlignLeft)
        self.cancelBtn.setMinimumSize(QtCore.QSize(60, 30))
        self.cancelBtn.setStyleSheet(CANC_StyleSheet)
        self.cancelBtn.setObjectName("cancel")
        self.cancelBtn.setAccessibleName("cancel")
        self.btn_horzlay.addWidget(self.cancelBtn, 1, QtCore.Qt.AlignRight)
        self.vertlay.addLayout(self.btn_horzlay)


class DefineFrame(_BotFrameMsg):
    """
    This frame takes in a word and diplay it's
    definitions according to the different Part Of Speech.

    Inherits:
        _BotFrameMsg
    """

    @QtCore.pyqtSlot(ChatBox, str)
    def __init__(self, parent: ChatBox, word: str) -> None:
        super().__init__(parent)
        self.word = word
        self._response = None
        self.set_heading(word.capitalize())

    @QtCore.pyqtSlot(dict)
    def set_response(self, response: dict):
        self._response = response

    def apply(self):
        if self._response is None or "title" in self._response.keys():
            self.set_response(
                "Can't fetch any definition for the word '{}'".format(self.word)
            )
            self.not_found = QtWidgets.QLabel(self._response, self)
            self.not_found.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.vertlay.addWidget(self.not_found)
            return
        self.def_label = QtWidgets.QLabel(self)
        self.def_label.setFixedWidth(600)
        self.def_label.setWordWrap(True)
        fnt = self.def_label.font()
        fnt.setPointSize(12)
        self.def_label.setFont(fnt)
        full_def = DEFINE_Style
        synonyms = []

        for i, meaning in enumerate(self._response["meanings"]):
            if i == 3:
                break  # We need not to add too many definitions
            full_def += (
                '<h3 class="pos">' + meaning["partOfSpeech"].capitalize() + "</h3>"
            )

            for j, definition in enumerate(meaning["definitions"]):
                if j == 3:
                    break
                full_def += (
                    '<p><span class="def">' + definition["definition"] + "</span><br/>"
                )

                if "example" in definition.keys():
                    full_def += '<span class="ex">' + definition["example"] + "</span>"
                if "synonyms" in definition.keys():
                    synonyms.extend(definition["synonyms"])
                full_def += "</p>"

            if (synonyms := set(synonyms)) != set():
                full_def += "<strong>Synonyms :</strong>  " + ", ".join(synonyms)
            synonyms = []

        # We need to predict the height of the widget for the animation.
        fm = self.def_label.fontMetrics()
        rect = fm.boundingRect(
            QtCore.QRect(0, 0, 600, 100), QtCore.Qt.TextFlag.TextWordWrap, full_def
        )
        self._height += rect.height() + 100  # Noticed there was an error of 100px
        self.def_label.setText(full_def)
        self.vertlay.addWidget(self.def_label)


class NoteAddFrame(_BotFrameMsg):
    """
    This frame helps user to add a new note. WoW

    Inherits:
        _BotFrameMsg
    """

    @QtCore.pyqtSlot(ChatBox)
    def __init__(self, chatbox: ChatBox) -> None:
        super().__init__(chatbox)
        self.titleEdit = QtWidgets.QLineEdit(self)
        self.descEdit = QtWidgets.QTextEdit(self)
        self.createBtn = QtWidgets.QPushButton("Create", self)
        self.cancelBtn = QtWidgets.QPushButton("Cancel", self)
        self.btn_horzlay = QtWidgets.QHBoxLayout()
        self.setStyleSheet(self.styleSheet() + BTN_StyleSheet + LNE_StyleSheet)

    def apply(self) -> None:
        self.set_heading("Create a note")
        self.setObjectName("noteAddFrame")
        fnt = self.titleEdit.font()
        fnt.setPointSize(15)
        self.vertlay.setSpacing(5)
        self.titleEdit.setFont(fnt)
        self.titleEdit.setPlaceholderText("Title")
        self.titleEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.titleEdit.setFixedHeight(60)
        self.titleEdit.setMaxLength(20)
        self.vertlay.addWidget(self.titleEdit)

        # We have to restrict the description of the to-do to
        # 200 characters as that's what our db is cappable of.
        def maxText() -> None:
            text = self.descEdit.toPlainText()
            if len(text) > 200:
                self.descEdit.setText(text[:200])
                self.descEdit.moveCursor(QtGui.QTextCursor.MoveOperation.End)

        self.descEdit.textChanged.connect(maxText)
        fnt.setPointSize(12)
        self.descEdit.setFont(fnt)
        self.descEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        # The text edit should show 5 lines at a time,
        # for greater amount of lines it will show a scrollbar
        self.descEdit.setAcceptRichText(False)
        self.descEdit.setPlaceholderText("Describe what your note is about")
        self.vertlay.addWidget(self.descEdit)

        def toggleCreateBtn() -> None:
            if len(self.descEdit.toPlainText()) == 0 or len(self.titleEdit.text()) == 0:
                self.createBtn.setDisabled(True)
                return
            else:
                self.createBtn.setEnabled(True)

        self.descEdit.textChanged.connect(toggleCreateBtn)
        self.titleEdit.textChanged.connect(toggleCreateBtn)
        self.titleEdit.setMaximumHeight(30)
        self.btn_horzlay.setObjectName("btn_horzlay")
        self.createBtn.setEnabled(False)
        self.createBtn.setStyleSheet(SAVE_StyleSheet)
        self.createBtn.setFixedSize(QtCore.QSize(60, 30))
        self.btn_horzlay.addWidget(self.createBtn, 0, QtCore.Qt.AlignLeft)
        self.cancelBtn.setStyleSheet(CANC_StyleSheet)

        def disableFrame() -> None:
            self.cancelBtn.setDisabled(True)
            self.createBtn.setDisabled(True)
            self.titleEdit.setDisabled(True)
            self.descEdit.setDisabled(True)

        self.cancelBtn.clicked.connect(disableFrame)
        self.createBtn.clicked.connect(disableFrame)
        self.cancelBtn.setFixedSize(QtCore.QSize(60, 30))
        self.btn_horzlay.addWidget(self.cancelBtn, 0, QtCore.Qt.AlignRight)
        self.vertlay.addLayout(self.btn_horzlay)
        self._height += 240  # Text-edits and Buttons


class NoteShowFrame(_BotFrameMsg):
    """
    This frame shows a pagination of all the notes created by user.

    Inherits:
        _BotFrameMsg
    """

    @QtCore.pyqtSlot(ChatBox)
    def __init__(self, chatbox: ChatBox) -> None:
        super().__init__(chatbox)
        self.notes = []
        self.setFixedWidth(500)
        self.descLabel = QtWidgets.QLabel(self)
        self._now_showing = 0
        self.next_btn = QtWidgets.QPushButton("❯", self)
        self.back_btn = QtWidgets.QPushButton("❮", self)
        self.del_btn = QtWidgets.QPushButton("🗑", self)
        self.cur_page = QtWidgets.QLabel("", self)
        self.horzlay = QtWidgets.QHBoxLayout()
        self.anim = QtCore.QPropertyAnimation(self, b"maximumHeight")
        self.setStyleSheet(self.styleSheet() + BTN_StyleSheet + LNE_StyleSheet)

    @QtCore.pyqtSlot(int, bool)
    def _show_note_number(self, number, animate=True) -> None:
        self._now_showing = number
        note = self.notes[number]
        self._heading.setText(note[0])
        self.descLabel.setText(note[1])
        fnt_mat = self.descLabel.fontMetrics()
        new_h = (
            fnt_mat.boundingRect(
                QtCore.QRect(0, 0, 400, 0), QtCore.Qt.TextFlag.TextWordWrap, note[1]
            ).height()
            + fnt_mat.height()
        )  # Because of an extra "<br>"
        if animate:
            self._toggle_pagination(False)
            self.anim.setStartValue(self._height)
            self.anim.setDuration(abs(self._height - 70 - new_h) * 10)
            self._height = 70 + new_h
            self.anim.setEndValue(self._height)
            self.anim.finished.connect(self.refresh_anim)
            self.anim.start()
        else:
            self._height = 70 + new_h
            self.setMaximumHeight(self._height)
        self.cur_page.setText(f"{number+1} / {len(self.notes)}")

    def refresh_anim(self):
        # Connected to the current animation finished signal, this function deletes old animation object and create a new one.
        self.anim.deleteLater()
        self.anim = QtCore.QPropertyAnimation(self, b"maximumHeight")
        self._toggle_pagination()

    @QtCore.pyqtSlot(bool)
    def _toggle_pagination(self, enabled=True):
        if len(self.notes) >= 1:
            self.back_btn.setEnabled(enabled)
            self.next_btn.setEnabled(enabled)
        else:
            self.back_btn.setEnabled(False)
            self.next_btn.setEnabled(False)

    def _show_next(self):
        self._show_note_number((self._now_showing + 1) % len(self.notes))

    def _show_back(self):
        self._show_note_number((self._now_showing - 1) % len(self.notes))

    @QtCore.pyqtSlot(str, str)
    def append_note(self, title, desc) -> None:
        self.notes.append((title, desc))

    @QtCore.pyqtSlot(int)
    def _delete_note(self, number) -> None:
        self.notes.pop(number)
        if len(self.notes) == 0:
            self.del_btn.setDisabled(True)
            self._heading.setText("Nothing to see here :(")
            self.descLabel.setText('Create a new note, try saying "Create a note."')
        else:
            self._show_next()

    def apply(self) -> None:
        self.setFixedWidth(500)
        # First we have to check wether user has any notes or not.
        if self.notes == []:
            self.set_heading("Nothing to see here :(")
            self.descLabel.setText('Create a new note, try saying "Create a note."')
            return
        self.set_heading(self.notes[0][0])
        fnt = QtGui.QFont("Ink Free", 10)
        self.descLabel.setFont(fnt)
        self.descLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.descLabel.setWordWrap(True)
        self.vertlay.addWidget(self.descLabel)
        self.next_btn.setFixedSize(QtCore.QSize(30, 30))
        self.next_btn.setStyleSheet(SAVE_StyleSheet)
        self.next_btn.clicked.connect(self._show_next)
        self.back_btn.setFixedSize(QtCore.QSize(30, 30))
        self.back_btn.setStyleSheet(SAVE_StyleSheet)
        self.back_btn.clicked.connect(self._show_back)
        self.del_btn.setFixedSize(QtCore.QSize(30, 30))
        self.del_btn.setStyleSheet(CANC_StyleSheet)
        self.del_btn.clicked.connect(lambda: self._delete_note(self._now_showing))
        self._height += 35
        self.cur_page.setStyleSheet("border : 0")
        self.cur_page.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        # If I found the note count in 1 then disable pagination
        if len(self.notes) <= 1:
            self._toggle_pagination()
        self.horzlay.addWidget(self.del_btn)
        self.horzlay.addWidget(self.cur_page)
        self.horzlay.addWidget(self.back_btn)
        self.horzlay.addWidget(self.next_btn)
        self.vertlay.addLayout(self.horzlay)
        # Show the note number 1 without any animation.
        self._show_note_number(0, False)
