# -*- coding: utf-8 -*-

import sys
import logging
import os
import random
from time import time
from PyQt4 import QtGui
from PyQt4.uic import loadUi

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

class Viewer(object):
    @property
    def db(self):
        return self.__db
    @db.setter
    def db(self, v):
        self.__db = v
    def __init__(self, parent = None):
        self.parent = parent
        logs = Logger(self.parent.logs)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logs)
        self.db = getdb('MongoDB')
        self.parent.fill.clicked.connect(self.fill)
        self.parent.clear.clicked.connect(self.parent.logs.clear)
        self.parent.addArtist.clicked.connect(self.addArtist)
        self.parent.removeArtist.clicked.connect(self.removeArtist)
        self.parent.addAlbum.clicked.connect(self.addAlbum)
        self.parent.removeAlbum.clicked.connect(self.removeAlbum)
        self.parent.artists.itemSelectionChanged.connect(self.fillAlbums)
        self.parent.albums.itemChanged.connect(self.albumChanged)
        self.fillArtists()
    def addArtist(self):
        artist = self.parent.artist.text()
        self.artists.addTopLevelItem(QtGui.QTreeWidgetItem([artist]))
        self.db.set({'name': str(artist)})
    def removeArtist(self):
        artist = self.parent.artists.selectedItems()[0]
        self.parent.artists.takeTopLevelItem(
            self.parent.artists.indexOfTopLevelItem(artist)
        )
        self.db.remove({'name': str(artist.text(0))})
    def addAlbum(self):
        year = self.parent.year.text()
        title = self.parent.title.text()
        borrowed = self.parent.borrowed.checkState()
        item = QtGui.QTreeWidgetItem([year, title])
        item.setCheckState(2, borrowed)
        self.parent.albums.addTopLevelItem(item)
        self.db.update(
            {'name': str(self.parent.artists.selectedItems()[0].text(0))},
            {
                '$push': {
                    'albums': {
                        'name': str(title),
                        'year': str(year),
                        'borrowed': bool(borrowed)
                    }
                }
            }
        )
    def removeAlbum(self):
        artist = str(self.parent.artists.selectedItems()[0].text(0))
        album = self.parent.albums.selectedItems()[0]
        self.parent.albums.takeTopLevelItem(
            self.parent.albums.indexOfTopLevelItem(album)
        )
        self.db.update(
            {'name': artist},
            {'$pull': {'albums': {'name': str(album.text(1))}}}
        )
    def fillArtists(self):
        for data in self.db.get(None, {'name':1}):
            self.parent.artists.addTopLevelItem(
                QtGui.QTreeWidgetItem([data['name']])
            )
    def fillAlbums(self):
        self.parent.albums.clear()
        artist = str(self.parent.artists.selectedItems()[0].text(0))
        for data in self.db.get_one({'name': artist}, {'albums': 1})['albums']:
            try:
                item = QtGui.QTreeWidgetItem([data['year'], data['name']])
                item.setCheckState(2, data['borrowed'] and 2)
                self.parent.albums.addTopLevelItem(item)
            except KeyError:
                pass
    def albumChanged(self, item, c):
        if c == 2:
            self.db.update(
                {
                    'name': str(self.parent.artists.selectedItems()[0].text(0)),
                    'albums.year': str(item.text(0)),
                    'albums.name': str(item.text(1))
                },
                {
                    '$set': {'albums.$.borrowed': bool(item.checkState(2))}
                }
            )
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

class Logger(logging.Handler):
    def __init__(self, parent = None, level = logging.DEBUG):
        logging.Handler.__init__(self, level)
        self.parent = parent
    def emit(self, record):
        self.parent.append(record.msg)
    def handle(self, record):
        logging.Handler.handle(self, record)

def run():
    app = QtGui.QApplication(sys.argv)
    main = loadUi('9.ui')
    a = Viewer(main)
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()
