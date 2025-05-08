from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Assistant")
current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

def TempDirectoryPath(Filename):
    return rf'{TempDirPath}\{Filename}'

def GraphicsDirectoryPath(Filename):
    return rf'{GraphicsDirPath}\{Filename}'

class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)
        
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(QColor(Qt.blue))
        self.chat_text_edit.setCurrentCharFormat(text_color_text)
        
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        movie.setScaledSize(QSize(400, 270))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)
        
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.start(500)
        
    def loadMessages(self):
        with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            if messages:
                self.addMessage(message=messages, color='white')

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        stacked_widget = QStackedWidget(self)
        chat_section = ChatSection()
        stacked_widget.addWidget(chat_section)
        
        self.setCentralWidget(stacked_widget)
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: black;")

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()
