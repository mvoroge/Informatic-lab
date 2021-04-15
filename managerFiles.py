import os
from shutil import copy2, move
from functools import partial

from PyQt5.QtCore import QModelIndex, QDir
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction, QFileDialog, QAbstractItemView, QLineEdit, QWidget, QGridLayout, QPushButton, \
    QTreeView, QFileSystemModel, QMainWindow


class MyMainWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.config_window()
        self.create_widgets()
        self.config_widgets()
        self.create_menubar()
        self.bind_widgets()
        self.show_widgets()

    def config_window(self):
        self.setWindowTitle('DirectoPy')
        self.setMinimumHeight(600)
        self.setMinimumWidth(1000)

    def create_widgets(self):
        self.central_widget = QWidget()
        self.main_layout = QGridLayout()
        self.moveup_button = QPushButton('Collapse all', self)
        self.goto_lineedit = QLineEdit('', self)
        self.goto_button = QPushButton('Go', self)
        self.folder_view = QTreeView(self)
        self.file_view = QTreeView(self)
        self.folder_model = QFileSystemModel(self)
        self.file_model = QFileSystemModel(self)

    def config_widgets(self):
        self.main_layout.addWidget(self.moveup_button, 0, 0)
        self.main_layout.addWidget(self.goto_lineedit, 0, 1, 1, 2)
        self.main_layout.addWidget(self.goto_button, 0, 3)
        self.main_layout.addWidget(self.folder_view, 1, 0, 1, 2)
        self.main_layout.addWidget(self.file_view, 1, 2, 1, 2)

        self.central_widget.setLayout(self.main_layout)

        # Кнопка "вверх"
        self.moveup_button.setMaximumWidth(100)

        # Кнопка "перейти"
        self.goto_button.setMaximumWidth(70)
        self.setCentralWidget(self.central_widget)
        # панели
        self.folder_model.setRootPath(None)
        self.folder_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        self.folder_view.setModel(self.folder_model)
        self.folder_view.setRootIndex(self.folder_model.index(None))
        self.folder_view.clicked[QModelIndex].connect(self.clicked_onfolder)
        self.folder_view.hideColumn(1)
        self.folder_view.hideColumn(2)
        self.folder_view.hideColumn(3)

        self.file_model.setFilter(QDir.Files)
        self.file_view.setModel(self.file_model)
        self.file_model.setReadOnly(False)
        self.file_view.setColumnWidth(0, 200)
        self.file_view.setSelectionMode(QAbstractItemView.ExtendedSelection)

    # открытие папки при нажати на неё в окне папок
    def clicked_onfolder(self, index):
        selection_model = self.folder_view.selectionModel()
        index = selection_model.currentIndex()
        dir_path = self.folder_model.filePath(index)
        self.file_model.setRootPath(dir_path)
        self.file_view.setRootIndex(self.file_model.index(dir_path))

    # ф-я открытия нового файла
    def open_file(self):
        index = self.file_view.selectedIndexes()
        if not index:
            return
        else:
            index = index[0]
        file_path = self.file_model.filePath(index).replace('/', '\\')
        print(file_path)
        self.file_view.update()

    # ф-я создания нового файла
    def new_file(self):
        global file_name
        index = self.folder_view.selectedIndexes()
        if len(index) > 0:
            path = self.folder_model.filePath(index[0])
            for i in range(1, 9999999999999999):
                if not os.path.isfile(os.path.join(path, "newfile{}.txt".format(i))):
                    file_name = os.path.join(path, "newfile{}.txt".format(i))
                    break
            file_name = os.path.abspath(file_name)
            open(file_name, 'w').close()
        else:
            print("Please, select folder")

    # ф-я удаления файла
    def delete_file(self):
        indexes = self.file_view.selectedIndexes()
        for i in indexes:
            self.file_model.remove(i)

    # ф-я переименования файла
    def rename_file(self):
        index = self.file_view.selectedIndexes()
        if not index:
            return
        else:
            index = index[0]
        self.file_view.edit(index)

    # ф-я копирования файла
    def copy_file(self):
        print("COPY")
        ask = QFileDialog.getExistingDirectory(self, "Open Directory", "C:\\",
                                               QFileDialog.ShowDirsOnly |
                                               QFileDialog.DontResolveSymlinks)
        new_path = ask.replace('\\', '/')
        indexes = self.file_view.selectedIndexes()[::4]
        for i in indexes:
            new_filename = new_path + '/' + self.file_model.fileName(i)
            copy2(self.file_model.filePath(i), new_filename)

    # ф-я возвращения к корню пути
    def colapse(self):
        self.folder_view.collapseAll()

    # ф-я перемещения в заданную директорию
    def go_to(self):
        dir_path = self.goto_lineedit.text().replace('\\', '/')
        print(dir_path)
        self.file_model.setRootPath(dir_path)
        self.file_view.setRootIndex(self.file_model.index(dir_path))

        #self.file_model.setRootPath()

    # ф-я перемещения файла
    def move_file(self):
        print("MOVE")
        ask = QFileDialog.getExistingDirectory(self, "Open Directory", "C:\\",
                                               QFileDialog.ShowDirsOnly |
                                               QFileDialog.DontResolveSymlinks)
        if ask == '':
            return
        new_path = ask.replace('\\', '/')
        indexes = self.file_view.selectedIndexes()[::4]
        for i in indexes:
            new_filename = new_path + '/' + self.file_model.fileName(i)
            move(self.file_model.filePath(i), new_filename)

    # ф-я создания новой папки
    def new_folder(self):
        global file_name
        index = self.folder_view.selectedIndexes()
        if len(index) > 0:
            path = self.folder_model.filePath(index[0])
            for i in range(1, 9999999999999999):
                if not os.path.isdir(os.path.join(path, "newfolder{}".format(i))):
                    file_name = os.path.join(path, "newfolder{}".format(i))
                    break
            file_name = os.path.abspath(file_name)
            os.mkdir(file_name)
        else:
            print("Please, select folder")

    # ф-я удаления папки
    def delete_folder(self):
        indexes = self.folder_view.selectedIndexes()
        for i in indexes:
            self.folder_model.remove(i)

    # ф-я переименования папки
    def rename_folder(self):
        index = self.folder_view.selectedIndexes()
        if not index:
            return
        else:
            index = index[0]
        self.folder_view.edit(index)

    # ф-я закрытия окна файлового менеджера
    def exit_application(self):
       print("EXIT")
       self.close()

    # задавание функции каждой кнопке
    def bind_widgets(self):
        self.open_file_action.triggered.connect(self.open_file)
        self.new_file_action.triggered.connect(self.new_file)
        self.delete_file_action.triggered.connect(self.delete_file)
        self.rename_file_action.triggered.connect(self.rename_file)
        self.copy_file_action.triggered.connect(self.copy_file)
        self.move_file_action.triggered.connect(self.move_file)
        self.exit_action.triggered.connect(self.exit_application)
        self.new_folder_action.triggered.connect(self.new_folder)
        self.delete_folder_action.triggered.connect(self.delete_folder)
        self.rename_folder_action.triggered.connect(self.rename_folder)


        self.goto_button.clicked.connect(partial(self.go_to))
        self.moveup_button.clicked.connect(partial(self.colapse))

    # создание меню
    def create_menubar(self):

        self.exit_action = QAction('Exit', self)
        self.exit_action.setShortcut('Ctrl+Q')

        self.new_file_action = QAction('New file', self)
        self.new_file_action.setShortcut('F4')

        self.open_file_action = QAction('Open file', self)
        self.open_file_action.setShortcut('F3')

        self.rename_file_action = QAction('Rename file', self)
        self.rename_file_action.setShortcut('F2')

        self.delete_file_action = QAction('Remove file', self)
        self.delete_file_action.setShortcut(QKeySequence.Delete)

        self.copy_file_action = QAction('Copy folder...', self)
        self.copy_file_action.setShortcut(QKeySequence.Copy)

        self.move_file_action = QAction('Move folder...', self)
        self.move_file_action.setShortcut(QKeySequence.Cut)

        self.new_folder_action = QAction('New folder', self)
        self.new_folder_action.setShortcut('Ctrl+Shift+N')

        self.delete_folder_action = QAction('Delete folder', self)
        self.delete_folder_action.setShortcut('Ctrl+Shift+Del')

        self.rename_folder_action = QAction('Rename folder', self)
        self.rename_folder_action.setShortcut('Ctrl+Shift+R')

        self.menubar = self.menuBar()
        self.file_menu = self.menubar.addMenu('File')
        self.file_menu.addAction(self.new_file_action)
        self.file_menu.addAction(self.open_file_action)
        self.file_menu.addAction(self.rename_file_action)
        self.file_menu.addAction(self.delete_file_action)
        self.file_menu.addAction(self.copy_file_action)
        self.file_menu.addAction(self.move_file_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        self.folder_menu = self.menubar.addMenu('Folder')
        self.folder_menu.addAction(self.new_folder_action)
        self.folder_menu.addAction(self.delete_folder_action)
        self.folder_menu.addAction(self.rename_folder_action)

    def show_widgets(self):
        self.setLayout(self.main_layout)
