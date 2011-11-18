# -*- coding: utf-8 -*-

import sys
import logging
import os
import random
from time import time
from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSignal

logger = logging.getLogger('z7')

class MongoDB(object):
    def __init__(self):
        from pymongo import Connection
        s = time()
        conn = Connection()
        self.db = conn.z7.artists
        logger.info('MongoDB: Loaded in {0} seconds.'.format(time() - s))
    def get_one(self, *query):
        if query == None:
            s = time()
            r = self.db.find_one()
            rr = time() - s
        else:
            s = time()
            r = self.db.find_one(*query)
            rr = time() - s
        logger.info('MongoDB: Got one record in {0} seconds.'.format(rr))
        return r
    def get(self, *query):
        if query == None:
            s = time()
            r = self.db.find()
            rr = time() - s
        else:
            s = time()
            r = self.db.find(*query)
            rr = time() - s
        logger.info(
            'MongoDB: Got {0} records in {1} seconds.'.format(r.count(), rr)
        )
        return r
    def set(self, values):
        s = time()
        self.db.insert(values)
        logger.info('MongoDB: Added {0} records in {1} seconds.'.format(
            len(values), time() - s
        ))
    def update(self, *query):
        s = time()
        self.db.update(*query)
        logger.info(
            'MongoDB: Updated a record in {0} seconds.'.format(time() - s)
        )
    def remove(self, item):
        s = time()
        self.db.remove(item)
        logger.info(
            'MongoDB: Removed a record in {0} seconds.'.format(time() - s)
        )

class CouchDB(object):
    def __init__(self):
        pass
    def get_one(self, item):
        pass
    def get(self, item):
        pass
    def set(self, item, value):
        pass
    def delete(self, item):
        pass

class Redis(object):
    def __init__(self):
        pass
    def get_one(self, item):
        pass
    def get(self, item):
        pass
    def set(self, item, value):
        pass
    def delete(self, item):
        pass

def getdb(name):
    return getattr(
        __import__(__name__, globals(), locals(), [name], -1), name
    )()

class Adder(QtGui.QWidget):
    add = pyqtSignal(str)
    remove = pyqtSignal()
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.label = QtGui.QLineEdit()
        self.button = QtGui.QPushButton('Add')
        self.button.clicked.connect(self.clicked)
        self.sbutton = QtGui.QPushButton('Remove')
        self.sbutton.clicked.connect(self.remove)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addWidget(self.sbutton)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
    def clicked(self):
        self.add.emit(self.label.text())

class Menu(QtGui.QWidget):
    clear = pyqtSignal()
    fill = pyqtSignal()
    dbChanged = pyqtSignal(str)
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.buttons = QtGui.QButtonGroup()
        mongo = QtGui.QRadioButton('MongoDB')
        mongo.setChecked(True)
        couch = QtGui.QRadioButton('CouchDB')
        redis = QtGui.QRadioButton('Redis')
        self.buttons.addButton(mongo)
        self.buttons.addButton(couch)
        self.buttons.addButton(redis)
        self.buttons.buttonClicked.connect(self.clicked)
        self.buttonsL = QtGui.QVBoxLayout()
        self.buttonsL.addWidget(mongo)
        self.buttonsL.addWidget(couch)
        self.buttonsL.addWidget(redis)
        groupbox = QtGui.QGroupBox('DB type')
        groupbox.setLayout(self.buttonsL)
        clear = QtGui.QPushButton('Clear')
        clear.clicked.connect(self.clear)
        fill = QtGui.QPushButton('Fill')
        fill.clicked.connect(self.fill)
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(groupbox)
        layout.addWidget(clear)
        layout.addWidget(fill)
        self.setLayout(layout)
    def clicked(self, button):
        self.dbChanged.emit(str(button.text()))

class Viewer(QtGui.QWidget):
    @property
    def db(self):
        return self.__db
    @db.setter
    def db(self, v):
        self.__db = v
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.artists = QtGui.QTreeWidget()
        self.artists.setHeaderLabels(['Artist'])
        self.artists.setIndentation(0)
        self.artists.itemSelectionChanged.connect(self.fillAlbums)
        artistsAdder = Adder()
        artistsAdder.add.connect(self.addArtist)
        artistsAdder.remove.connect(self.removeArtist)
        artistsL = QtGui.QVBoxLayout()
        artistsL.addWidget(self.artists)
        artistsL.addWidget(artistsAdder)
        self.albums = QtGui.QTreeWidget()
        self.albums.setHeaderLabels(['Year', 'Album', 'Borrowed'])
        self.albums.setIndentation(0)
        self.albums.itemChanged.connect(self.albumChanged)
        albumsAdder = Adder()
        albumsAdder.add.connect(self.addAlbum)
        albumsAdder.remove.connect(self.removeAlbum)
        albumsL = QtGui.QVBoxLayout()
        albumsL.addWidget(self.albums)
        albumsL.addWidget(albumsAdder)
        dbL = QtGui.QHBoxLayout()
        dbL.addLayout(artistsL)
        dbL.addLayout(albumsL)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(dbL)
        self.setLayout(layout)
    def addArtist(self, artist):
        self.artists.addTopLevelItem(QtGui.QTreeWidgetItem([artist]))
        self.db.set({'name': str(artist)})
    def removeArtist(self):
        artist = self.artists.selectedItems()[0]
        self.artists.takeTopLevelItem(self.artists.indexOfTopLevelItem(artist))
        self.db.remove({'name': str(artist.text(0))})
    def addAlbum(self, album):
        data = album.split(';')
        item = QtGui.QTreeWidgetItem(data[:-1])
        item.setCheckState(2, data[-1] == 'yes' and 2)
        self.albums.addTopLevelItem(item)
        self.db.update(
            {'artist': str(self.artists.selectedItems()[0].text(0))},
            {
                'album': str(data[0]),
                'year': str(data[1]),
                'borrowed': bool(data[-1] == 'yes')
            }
        )
    def removeAlbum(self):
        artist = str(self.artists.selectedItems()[0].text(0))
        album = self.albums.selectedItems()[0]
        self.albums.takeTopLevelItem(self.albums.indexOfTopLevelItem(album))
        self.db.update(
            {'name': artist},
            {'$pull': {'albums': {'name': str(album.text(1))}}}
        )
    def fillArtists(self):
        for data in self.db.get(None, {'name':1}):
            self.artists.addTopLevelItem(
                QtGui.QTreeWidgetItem([data['name']])
            )
    def fillAlbums(self):
        self.albums.clear()
        artist = str(self.artists.selectedItems()[0].text(0))
        for data in self.db.get_one({'name': artist}, {'albums': 1})['albums']:
            try:
                item = QtGui.QTreeWidgetItem([data['year'], data['name']])
                item.setCheckState(2, data['borrowed'] and 2)
                self.albums.addTopLevelItem(item)
            except KeyError:
                pass
    def albumChanged(self, item, c):
        if c == 2:
            data = bool(item.checkState(2))
            self.db.update(
                {
                    'name': str(self.artists.selectedItems()[0].text(0)),
                    'albums.year': str(item.text(0)),
                    'albums.name': str(item.text(1))
                },
                {
                    '$set': {'albums.$.borrowed': data}
                }
            )

class Logger(QtGui.QTextBrowser, logging.Handler):
    def __init__(self, level = logging.DEBUG, parent = None):
        QtGui.QTextBrowser.__init__(self, parent)
        logging.Handler.__init__(self, level)
    def emit(self, record):
        self.append(record.msg)
    def handle(self, record):
        logging.Handler.handle(self, record)

class Editor(QtGui.QWidget):
    dbChanged = pyqtSignal(str)
    fill = pyqtSignal()
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        menu = Menu()
        menu.dbChanged.connect(self.dbChanged)
        logs = Logger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logs)
        menu.clear.connect(logs.clear)
        menu.fill.connect(self.fill)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(logs)
        layout.addWidget(menu)
        self.setLayout(layout)

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        #super(type(self), self).__init__(self)
        editor = Editor()
        editor.fill.connect(self.fill)
        self.db = getdb('MongoDB')
        self.viewer = Viewer()
        self.viewer.db = self.db
        self.viewer.fillArtists()
        editor.dbChanged.connect(self.getdb)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.viewer)
        layout.addWidget(editor)
        widget = QtGui.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    def getdb(self, name):
        self.db = getdb(str(name))
        self.viewer.db = self.db
    def fill(self):
        data = list()
        d = '/mnt/music'
        dirs = [f for f in os.listdir(d) if os.path.isdir(os.path.join(d, f))]
        for di in dirs:
            da = os.path.join(d, di)
            subdirs = [
                f for f in os.listdir(da) if os.path.isdir(os.path.join(da, f))
            ]
            albums = list()
            for sd in subdirs:
                s = sd.split(' - ', 1)
                try:
                    albums.append({
                        'name': s[1],
                        'year': s[0],
                        'borrowed': bool(random.randrange(2))
                    })
                except IndexError:
                    pass
            if albums:
                data.append({
                    'name': di,
                    'albums': albums
                })
        self.db.set(data)

def run():
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()
