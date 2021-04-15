from time import sleep
from datetime import datetime
import managerFiles
from PyQt5.QtCore import QTime, QTimer, QThread, pyqtSignal
from PyQt5.Qt import Qt
from psutil import disk_usage, disk_partitions, virtual_memory
from sys import exit, argv
from PyQt5.QtWidgets import QMainWindow, QWidget, QDesktopWidget, QApplication, QLabel, QPushButton, QMessageBox


def totalAndFree(step):
    diskC = "C:"
    diskD = "D:"
    free1 = disk_usage(diskC).free/(1024 * 1024 * 1024)
    total1 = disk_usage(diskC).total/(1024 * 1024 * 1024)
    free2 = disk_usage(diskD).free / (1024 * 1024 * 1024)
    total2 = disk_usage(diskD).total / (1024 * 1024 * 1024)
    diskone = f"{total1 + total2:.4} Gb on disk"
    disktwo = f"{free1 + free2:.4} Gb free on disk"
    if step == 1:
        return diskone
    elif step == 2:
        return disktwo


class newTime(QThread):
    def __init__(self, mainwindow, perent=None):
        super(newTime, self).__init__(perent)
        self.mainwindow = mainwindow

    # метод, который будет выполнять алгоритм в другом потоке
    def run(self):
        while True:
            self.mainwindow.labelTime.setText(datetime.now().strftime("%H:%M:%S"))
            sleep(1)


class newVirtualMemory(QThread):
    def __init__(self, mainwindow, perent=None):
        super(newVirtualMemory, self).__init__(perent)
        self.mainwindow = mainwindow

    # метод, который будет выполнять алгоритм в другом потоке
    def run(self):
        while True:
            self.mainwindow.labelVM.setText(f"{dict(virtual_memory()._asdict())['free'] / (1024*1024*1024):.4} Gb free")
            sleep(0.1)


# класс с информацией о дисках
class diskInfo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(600, 100)
        self.center()
        self.setWindowTitle("Disk Info")

        self.inf1 = QLabel(str(disk_partitions()[0]), self)
        self.inf1.resize(600, 20)
        self.inf1.move(0, 0)
        self.inf2 = QLabel(str(disk_partitions()[1]), self)
        self.inf2.resize(600, 20)
        self.inf2.move(0, 25)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


# класс с инфомацией о размере и заполненности жестких дисков (с обновлением инф-ции каждую 1 сек
class diskSize(QWidget):
    right_click = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(400, 100)
        self.center()
        self.setWindowTitle("Disk size")

        self.totalMemory = QLabel(str(totalAndFree(1)), self)
        self.totalMemory.resize(150, 20)
        self.totalMemory.move(0, 0)
        self.freeMemory = QLabel(str(totalAndFree(2)), self)
        self.freeMemory.resize(150, 20)
        self.freeMemory.move(0, 15)

        self.times = QLabel('At ' + QTime.currentTime().toString(), self)
        self.times.move(0, 35)

        self.btnOk = QPushButton(self)
        self.btnOk.move(150, 50)
        self.btnOk.resize(100, 25)
        self.btnOk.setText("Актуальное")
        self.btnOk.clicked.connect(self.tick)

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(3000)

    # Ф-я обновляющая значение текущей памяти  каждые 3 сек
    def tick(self):
        self.totalMemory.setText(str(totalAndFree(1)))
        self.freeMemory.setText(str(totalAndFree(2)))
        self.times.setText('At ' + QTime.currentTime().toString())

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def clickRight(self):
        self.msgBox = QMessageBox()
        self.msgBox.setIcon(QMessageBox.Information)
        self.msgBox.setText('Вы нажали правую кнопку мыши!')
        self.msgBox.setWindowTitle("MessageBox")
        self.msgBox.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.right_click.emit()
            self.clickRight()
            self.tick()


class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.resize(700, 500)
        self.center()
        self.setWindowTitle('disk')

        self.btnOk = QPushButton(self)
        self.btnOk.move(225, 200)
        self.btnOk.resize(100, 30)
        self.btnOk.setText("Объём памяти")
        self.btnOk.clicked.connect(self.btnSize)

        self.btnOk = QPushButton(self)
        self.btnOk.move(375, 200)
        self.btnOk.resize(150, 30)
        self.btnOk.setText("Информация о дисках")
        self.btnOk.clicked.connect(self.btnInfo)

        self.btnOk = QPushButton(self)
        self.btnOk.move(275, 300)
        self.btnOk.resize(150, 30)
        self.btnOk.setText("Файловый менеджер")
        self.btnOk.clicked.connect(self.btnFiles)

        self.labelTime = QLabel(self)
        self.labelTime.setText(datetime.now().strftime("%H:%M:%S"))
        self.labelTime.move(0, 5)

        self.labelVM = QLabel(self)
        self.labelVM.setText(f"{dict(virtual_memory()._asdict())['free'] / (1024*1024*1024):.4} Gb free")
        self.labelVM.move(0, 20)

        # Создаётся экзэмпляр класса
        self.showTime = newTime(mainwindow=self)
        self.showTime.start()

        # Создаётся экзэмпляр класса
        self.showVM = newVirtualMemory(mainwindow=self)
        self.showVM.start()

    # функции создания экземпляра разных классов и показа в отдельном окне
    def btnSize(self):
        self.w1 = diskSize()
        self.w1.show()

    def btnInfo(self):
        self.w2 = diskInfo()
        self.w2.show()

    def btnFiles(self):
        self.w3 = managerFiles.MyMainWindow()
        self.w3.show()

    # выравниеварие кна по центру
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


def diskApp():
    if __name__ == '__main__':
        app = QApplication(argv)
        ex = Example()
        ex.show()
        exit(app.exec())


diskApp()