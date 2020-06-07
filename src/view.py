import threading

SPEED = 15
MIN_HEIGHT = 200
MAX_HEIGHT = 984
import math
import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets, QtCore, QtGui, QtNetwork
import design  # Это наш конвертированный файл дизайна
from tcp import start_socket


class ClientApp(QtWidgets.QMainWindow, design.Ui_mainWindow):
    sig = QtCore.pyqtSignal()
    inProcess = False
    isOpen = False
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        self.counter = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.roll_step)

        self.sourcePicture = QtGui.QPixmap("res/3.png")
        self.setPicture = QtGui.QPixmap(self.sourcePicture.size())
        self.sig.connect(self.roll_start)
        start_socket(self)
        self.down = False
        self.roll_start()


    def setup_text(self, text, title):
        if (text == ""):
            self.down = False
        else:
            self.text_string = text
            self.title_string = title
            self.down = True
        self.sig.emit()

    def roll_step(self):
        height = self.roll.height()
        if (self.down and height < MAX_HEIGHT) or (not self.down and height > MIN_HEIGHT):
            step = math.ceil((MAX_HEIGHT - height) * SPEED / 250)
            height += (step if self.down else (-step - 1))
        else:
            self.timer.stop()
            self.inProcess = False
            if self.down:
                self.set_text()
                self.isOpen = True
            else:
                self.isOpen = False
        self.roll.setFixedHeight(height)
        self.set_opacity((height-MIN_HEIGHT)/(MAX_HEIGHT-MIN_HEIGHT))

    def set_opacity(self, opacity):
        self.setPicture.fill(QtCore.Qt.transparent)
        self.painter = QtGui.QPainter(self.setPicture)
        self.painter.setOpacity(opacity)
        self.painter.drawPixmap(0, 0, self.sourcePicture)
        self.painter.end()
        self.roll.setPixmap(self.setPicture)

    def roll_start(self):
        if not self.down:
            self.clear_roll()
        if self.isOpen and self.down:
            self.set_text()
        else:
            if self.inProcess:
                return
            self.inProcess = True
            self.roll.setFixedHeight(MIN_HEIGHT if self.down else MAX_HEIGHT)
            self.timer.start(1)

    def clear_roll(self):
        self.title_string = ""
        self.text_string = ""
        self.set_text()

    def set_text(self):
        self.set_title(self.title_string)
        self.set_main_text(self.text_string)

    def set_title(self, title_string):
        self.titleText.setText(title_string)

    def set_main_text(self, text_string):
        if len(text_string):
            font = self.mainText.font()
            rect = self.mainText.contentsRect()
            fontSize = 1
            while True:
                f = QtGui.QFont(font)
                f.setPixelSize(fontSize)
                r = QtGui.QFontMetrics(f).boundingRect(rect, QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap, text_string)
                if(r.height() <= rect.height() and r.width() <= rect.width()):
                    fontSize += 1
                else:
                    break
            f.setPixelSize(fontSize-1)
            self.mainText.setFont(f)
        self.mainText.setText(text_string)

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ClientApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

main()
