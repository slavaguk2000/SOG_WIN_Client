import threading

SPEED = 5
SHAKE_AMPLITUDE = 20
MIN_HEIGHT = 0
MAX_HEIGHT = 984 - SHAKE_AMPLITUDE
MIN_WIDTH = 0
MAX_WIDTH = 741
TIMER_TIMEOUT = 20


import math
import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets, QtCore, QtGui, QtNetwork
import design  # Это наш конвертированный файл дизайна
from tcp import start_socket

def d_ceil(num):
    new_num = math.ceil(num)
    if num < 0:
        new_num -= 1
    return new_num

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
        self.rollTimer = QtCore.QTimer()
        self.rollTimer.timeout.connect(self.roll_step)
        self.scriptTimer = QtCore.QTimer()
        self.scriptTimer.timeout.connect(self.script_step)
        if design.isFull:
            self.mainText.setStyleSheet("color: white")
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
        width = self.roll.width()
        if (self.down and width < MAX_WIDTH) or (not self.down and width > MIN_WIDTH):
            step = math.ceil((MAX_WIDTH - width) * SPEED / 10)
            width += (step if self.down else (-step - 1))
        else:
            self.rollTimer.stop()
            if self.down:
                self.target_height = MAX_HEIGHT + SHAKE_AMPLITUDE
                self.scriptTimer.start(TIMER_TIMEOUT)
            else:
                self.inProcess = False
        self.roll.setGeometry(QtCore.QRect(MAX_WIDTH-width, 0, width, MAX_HEIGHT))
        self.roll.setFixedWidth(width)

    def script_step(self):
        height = self.script.height()
        if (self.down and height != self.target_height) or (not self.down and height > MIN_HEIGHT):
            step = d_ceil((self.target_height - height) * SPEED / 10)
            height += (step if self.down else (-step - 1))
        else:
            amplitude = self.target_height - MAX_HEIGHT
            if amplitude == 0:
                self.scriptTimer.stop()
                if self.down:
                    self.set_text()
                    self.inProcess = False
                    self.isOpen = True
                else:
                    self.rollTimer.start(TIMER_TIMEOUT)
                    self.isOpen = False
            else:
                amplitude = int(amplitude / 2)
                print("new amplitude ", amplitude)
                self.target_height = MAX_HEIGHT - amplitude
        self.script.setFixedHeight(height)

    def roll_start(self):
        print("roll start")
        if not self.down:
            self.clear_roll()
        if (self.isOpen and self.down) or design.isFull:
            self.set_text()
        else:
            if self.inProcess:
                return
            self.inProcess = True
            self.roll.setFixedWidth(MIN_WIDTH if self.down else MAX_WIDTH)
            self.script.setFixedHeight(MIN_HEIGHT if self.down else MAX_HEIGHT)
            if self.down:
                print("rollT start")
                self.rollTimer.start(TIMER_TIMEOUT)
            else:
                print("scriptT start")
                self.target_height = int(MAX_HEIGHT)
                self.scriptTimer.start(TIMER_TIMEOUT)


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
    design.isFull = int(sys.argv[-2]) if len(sys.argv) > 2 else 0
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ClientApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

main()
