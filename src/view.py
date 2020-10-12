import math
import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets, QtCore, QtGui, QtNetwork
import design  # Это наш конвертированный файл дизайна
from tcp import start_socket, stop_socket

import config

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
    string_index = 0
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.counter = 0
        self.rollTimer = create_timer(self.roll_step)
        self.scriptTimer = create_timer(self.script_step)
        self.textTimer = create_timer(self.text_step)
        if config.isFull:
           self.mainText.setStyleSheet("color: white")
        self.sig.connect(self.roll_start)
        start_socket(self)
        self.script.setFixedWidth(config.MIN_WIDTH)
        self.roll.setFixedHeight(config.MIN_HEIGHT)
        self.destroyed.connect(stop_socket)		
		
		
    def keyPressEvent(self, e):
        if e.text() == ".":
            self.string_index += 1
            if self.string_index >= len(self.text_strings):
                self.string_index = 0
            self.set_text()

    def setup_text(self, text, title):
        self.string_index = 0
        self.text_strings = text.split(".")
        self.title_string = title
        self.down = text != ""
        self.set_text()

    def roll_end(self):
        if self.down:
            self.target_width = config.MAX_WIDTH+ config.SHAKE_AMPLITUDE
            self.scriptTimer.start(config.TIMER_TIMEOUT)
        else:
            self.inProcess = False

    def script_end(self):
        if self.down:
            self.set_text()
            self.target_alpha = 255
            self.textTimer.start(config.TIMER_TIMEOUT)
        else:
            self.target_height = config.MIN_HEIGHT
            self.rollTimer.start(config.TIMER_TIMEOUT)

    def setScriptWidth(self, width):
        self.script.setFixedWidth(width)

    def setRollHeight(self, height):
        self.roll.setGeometry(QtCore.QRect(0, config.yStart + (config.MAX_HEIGHT - height) / 2, config.MAX_WIDTH, height)) #from right
        self.roll.setFixedHeight(height)

    def set_roll_target(self, amplitude):
        self.target_height = config.MAX_HEIGHT - amplitude

    def set_script_target(self, amplitude):
        self.target_width = config.MAX_WIDTH - amplitude

    def core_step(self, demesion_get, target, end_target, timer, end_fun, set_demension_fun, set_new_target):
        demension = demesion_get()
        if (demension != target):
            step = d_ceil((target - demension) * config.SPEED / 10)
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
        self.core_step(self.roll.height, self.target_height, config.MAX_HEIGHT, self.rollTimer, self.roll_end, self.setRollHeight, self.set_roll_target)

    def script_step(self):
        self.core_step(self.script.width, self.target_width, config.MAX_WIDTH, self.scriptTimer, self.script_end, self.setScriptWidth, self.set_script_target)

    def text_step(self):
        if (self.alpha != self.target_alpha):
            self.alpha += d_ceil((self.target_alpha - self.alpha) * config.SPEED * config.SPEED_TEXT / 25)
            styleSheet = "background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, " + str(self.alpha / 255) + ")"
            for textLabel in [self.mainText, self.titleText]:
                textLabel.setStyleSheet(styleSheet)
        else:
            self.textTimer.stop()
            if self.down:
                self.isOpen = True
            else:
                self.isOpen = False
                self.target_width = config.MIN_WIDTH
                self.scriptTimer.start(config.TIMER_TIMEOUT)

    def roll_start(self):
        if (self.isOpen and self.down) or config.isFull or True:
            self.set_text()
        else:
            if self.down:
                self.target_height = config.MAX_HEIGHT + config.SHAKE_AMPLITUDE / 2
                self.rollTimer.start(config.TIMER_TIMEOUT)
            else:
                self.target_alpha = 0
                self.textTimer.start(config.TIMER_TIMEOUT)


    def set_text(self):
        self.set_title(self.title_string)
        self.set_main_text(self.text_strings[self.string_index])

    def set_title(self, title_string):
        self.titleText.setText(title_string)

    def set_main_text(self, text_string):
        if len(text_string):
            font = self.mainText.font()
            rect = self.mainText.geometry()
            fontSize = 1
            while True:
                f = QtGui.QFont(font)
                f.setPixelSize(fontSize)
                r = QtGui.QFontMetrics(f).boundingRect(rect, QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap, text_string)
                if(r.height() <= rect.height() and r.width() <= rect.width()):
                #if((r.height() <= int(761 - (int(design.y1 - ((design.x1 - design.x0) * 9 /16))))) and (r.width() <= rect.width())):
                    if fontSize < config.maxFontSize:
                        fontSize += 1   
                    else:
                        break                    
                else:
                    break
            f.setPixelSize(fontSize-1)
            self.mainText.setFont(f)
        self.mainText.setText(text_string)


def main():
    config.isFull = int(sys.argv[-2]) if len(sys.argv) > 2 else 0
    if not config.isFull:
        config.ySize /= 3
        config.ySize = int(config.ySize)
        config.yStart = 2 * config.ySize
        config.MAX_HEIGHT = config.HEIGHT - config.yStart - config.SHAKE_AMPLITUDE        
        config.x0 += 60
        config.xSize = config.WIDTH - 2*config.x0
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ClientApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

main()
