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

def create_timer(step_fun):
    timer = QtCore.QTimer()
    timer.timeout.connect(step_fun)
    return timer

class ClientApp(QtWidgets.QMainWindow, design.Ui_mainWindow):
    sig = QtCore.pyqtSignal()
    inProcess = False
    isOpen = False
    alpha = 0
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.counter = 0
        self.rollTimer = create_timer(self.roll_step)
        self.scriptTimer = create_timer(self.script_step)
        self.textTimer = create_timer(self.text_step)
        if design.isFull:
            self.mainText.setStyleSheet("color: white")
        self.sig.connect(self.roll_start)
        start_socket(self)
        self.roll.setFixedWidth(MIN_WIDTH)
        self.script.setFixedHeight(MIN_HEIGHT)

    def setup_text(self, text, title):
        self.text_string = text
        self.title_string = title
        self.down = text != ""
        self.sig.emit()

    def roll_end(self):
        if self.down:
            self.target_height = MAX_HEIGHT + SHAKE_AMPLITUDE
            self.scriptTimer.start(TIMER_TIMEOUT)
        else:
            self.inProcess = False

    def script_end(self):
        if self.down:
            self.set_text()
            self.target_alpha = 255
            self.textTimer.start(TIMER_TIMEOUT)
        else:
            self.target_width = MIN_WIDTH
            self.rollTimer.start(TIMER_TIMEOUT)

    def setScriptHeight(self, height):
        self.script.setFixedHeight(height)

    def setRollWidth(self, width):
        self.roll.setGeometry(QtCore.QRect(MAX_WIDTH - width, 0, width, MAX_HEIGHT))
        self.roll.setFixedWidth(width)

    def set_roll_target(self, amplitude):
        self.target_width = MAX_WIDTH - amplitude

    def set_script_target(self, amplitude):
        self.target_height = MAX_HEIGHT - amplitude

    def core_step(self, demesion_get, target, end_target, timer, end_fun, set_demension_fun, set_new_target):
        demension = demesion_get()
        if (demension != target):
            step = d_ceil((target - demension) * SPEED / 10)
            demension += step
        else:
            if self.down:
                amplitude = target - end_target
                if not amplitude:
                    timer.stop()
                    end_fun()
                else:
                    amplitude = int(amplitude / 2)
                    set_new_target(amplitude)
            else:
                timer.stop()
                end_fun()
        set_demension_fun(demension)

    def roll_step(self):
        self.core_step(self.roll.width, self.target_width, MAX_WIDTH, self.rollTimer, self.roll_end, self.setRollWidth, self.set_roll_target)

    def script_step(self):
        self.core_step(self.script.height, self.target_height, MAX_HEIGHT, self.scriptTimer, self.script_end, self.setScriptHeight, self.set_script_target)

    def text_step(self):
        if (self.alpha != self.target_alpha):
            self.alpha += d_ceil((self.target_alpha - self.alpha) * SPEED / 25)
            styleSheet = "background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, " + str(self.alpha / 255) + ")"
            for textLabel in [self.mainText, self.titleText]:
                textLabel.setStyleSheet(styleSheet)
        else:
            self.textTimer.stop()
            if self.down:
                self.isOpen = True
            else:
                self.isOpen = False
                self.target_height = MIN_HEIGHT
                self.scriptTimer.start(TIMER_TIMEOUT)

    def roll_start(self):
        if (self.isOpen and self.down) or design.isFull:
            self.set_text()
        else:
            if self.down:
                self.target_width = MAX_WIDTH + SHAKE_AMPLITUDE / 2
                self.rollTimer.start(TIMER_TIMEOUT)
            else:
                self.target_alpha = 0
                self.textTimer.start(TIMER_TIMEOUT)


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
