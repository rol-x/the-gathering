from __init__ import *
from datamining import read_query

def sizentitle(win):
    win.setFixedSize(640, 480)
    win.setGeometry(200,200,640,480)
    win.setWindowTitle("Data Access Module")

def exitapp(window):
    window.close()

def button(win, text, func, movx, movy, sizex, sizey):
    button1 = QPushButton(win)
    button1.setText(text)
    if func != None:
        button1.clicked.connect(lambda: func(win))
    button1.move(movx, movy)
    button1.resize(sizex, sizey)
    return button1

def label(win, text, font, movx, movy, size):
    label = QLabel(win)
    label.setText(text)
    if font != None:
        label.setFont(QFont(font[0], font[1]))
    label.move(movx,movy)
    if type(size) == int:
        label.resize(label.sizeHint())
    else:
        label.resize(size[0],size[1])
    return label

def combobox(win, connection, query, movx, movy):
    result = read_query(connection, query)
    choices = [""]
    for i in result:
        choices.append(i[0])
    choice = QComboBox(win)
    for i in choices:
        choice.addItem(i)
    choice.move(movx, movy)
    return choice