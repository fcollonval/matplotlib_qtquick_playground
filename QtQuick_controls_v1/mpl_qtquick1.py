"""
Series of data are loaded from a .csv file, and their names are
displayed in a checkable list view. The user can select the series
it wants from the list and plot them on a matplotlib canvas.
Use the sample .csv file that comes with the script for an example
of data series.

[2016-11-05] Convert to QtQuick 2.0 - QtQuick Controls 1.0
[2016-11-01] Update to PyQt5.6 and python 3.5

Frederic Collonval (fcollonval@gmail.com)

Inspired from the work of Eli Bendersky (eliben@gmail.com):
https://github.com/eliben/code-for-blog/tree/master/2009/pyqt_dataplot_demo

License: MIT License
Last modified: 2016-11-05
"""
import sys, os, csv
from PyQt5.QtCore import QAbstractListModel, QModelIndex, QObject, QSize, Qt, QUrl, QVariant, pyqtProperty, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QGuiApplication, QColor, QImage, QPixmap
# from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine, qmlRegisterType
from PyQt5.QtQuick import QQuickImageProvider

import matplotlib
matplotlib.use('Agg')
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
# from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np

class DataSerie(object):

    def __init__(self, name, data, selected=False):
        self._name = name
        self._data = data
        self._selected = selected
    
    def name(self):
        return self._name
    
    def selected(self):
        return self._selected
        
    def data(self):
        return self._data

class DataSeriesModel(QAbstractListModel):

    # Define role enum
    SelectedRole = Qt.UserRole
    NameRole = Qt.UserRole + 1
    DataRole = Qt.UserRole + 2

    _roles = {
        SelectedRole : b"selected",
        NameRole : b"name",
        DataRole : b"data"
    }
    
    lengthDataChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        
        self._data_series = list()
        self._length_data = 0
    
    @pyqtProperty(int, notify=lengthDataChanged)
    def lengthData(self):
        return self._length_data
    
    @lengthData.setter
    def lengthData(self, length):
        if self._length_data != length:
            self._length_data = length
            self.lengthDataChanged.emit()

    def roleNames(self):
        return self._roles
    
    def load_from_file(self, filename=None):
        self._data_series.clear()
        self._length_data = 0

        if filename:
            with open(filename, 'r') as f:
                for line in csv.reader(f):
                    series = DataSerie(line[0], 
                                       [i for i in map(int, line[1:])])
                    self.add_data(series)
                    
    def add_data(self, data_series):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._data_series.append(data_series)
        self.lengthData = max(self.lengthData, len(data_series.data()))
        self.endInsertRows()
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._data_series)
        
    def data(self, index, role=Qt.DisplayRole):
        if(index.row() < 0 or index.row() >= len(self._data_series)):
            return QVariant()
        
        series = self._data_series[index.row()]
        
        if role == self.SelectedRole:
            return series.selected()
        elif role == self.NameRole:
            return series.name()
        elif role == self.DataRole:
            return series.data()
        
        return QVariant()
    
    def setData(self, index, value, role=Qt.EditRole):
        if(index.row() < 0 or index.row() >= len(self._data_series)):
            return False
        
        series = self._data_series[index.row()]
        
        if role == self.SelectedRole:
            series._selected = value
            self.dataChanged.emit(index, index, [role,])
            return True
                
        return False
                    
class Form(QObject):

    xFromChanged = pyqtSignal()
    xToChanged = pyqtSignal()
    legendChanged = pyqtSignal()
    statusTextChanged = pyqtSignal()
    stateChanged = pyqtSignal()

    def __init__(self, data=None):
        QObject.__init__(self)
        
        self._status_text = "Please load a data file"
        
        self._filename = ""
        self._x_from = 0
        self._x_to = 1
        self._legend = False
        
        # default dpi=80, so size = (480, 320)
        self.figure = plt.figure(figsize=(6.0, 4.0))
        self.figure.set_facecolor('white')
        self.axes = self.figure.add_subplot(111)
        
        self._data = data

    @pyqtProperty('QString', notify=statusTextChanged)
    def statusText(self):
        return self._status_text
    
    @statusText.setter
    def statusText(self, text):
        if self._status_text != text:
            self._status_text = text
            self.statusTextChanged.emit()
        
    @pyqtProperty('QString')
    def filename(self):
        return self._filename
    
    @filename.setter
    def filename(self, filename):
        if filename:
            filename = QUrl(filename).toLocalFile()
            if filename != self._filename:
                self._filename = filename
                self._data.load_from_file(filename)
                self.statusText = "Loaded " + filename
                self.xTo = self._data.lengthData

    @pyqtProperty(int, notify=xFromChanged)
    def xFrom(self):
        return self._x_from
    
    @xFrom.setter
    def xFrom(self, x_from):
        x_from = int(x_from)
        if self._x_from != x_from:
            self._x_from = x_from
            self.axes.set_xlim(left=self._x_from)
            self.xFromChanged.emit()
        
    @pyqtProperty(int, notify=xToChanged)
    def xTo(self):
        return self._x_to
    
    @xTo.setter
    def xTo(self, x_to):
        x_to = int(x_to)
        if self._x_to != x_to:
            self._x_to = x_to
            self.axes.set_xlim(right=self._x_to)
            self.xToChanged.emit()
        
    @pyqtProperty(bool, notify=legendChanged)
    def legend(self):
        return self._legend
    
    @legend.setter
    def legend(self, legend):
        if self._legend != legend:
            self._legend = legend
            if self._legend:
                self.axes.legend()
            else:
                leg = self.axes.get_legend()
                if leg is not None:
                    leg.remove()
            self.legendChanged.emit()
    
    @pyqtProperty('QString', constant=True)
    def about(self):
        msg = __doc__
        return msg.strip()
        
    
    @pyqtSlot()
    def update_figure(self):
        self.axes.clear()
        self.axes.grid(True)
        
        has_series = False

        for row in range(self._data.rowCount()):
            model_index = self._data.index(row, 0)
            checked = self._data.data(model_index, DataSeriesModel.SelectedRole)
            
            if checked:
                has_series = True
                name = self._data.data(model_index, DataSeriesModel.NameRole)                
                values = self._data.data(model_index, DataSeriesModel.DataRole)
                
                self.axes.plot(range(len(values)), values, 'o-', label=name)

        self.axes.set_xlim((self.xFrom, self.xTo))
        if has_series and self.legend:
            self.axes.legend()
        # self.canvas.draw()
        
        self.stateChanged.emit()

    # def create_status_bar(self):
        # self.status_text = QLabel("Please load a data file")
        # self.statusBar().addWidget(self.status_text, 1)

class MatplotlibImageProvider(QQuickImageProvider):

    def __init__(self, fig, img_type = QQuickImageProvider.Pixmap):
        self._fig = fig
        QQuickImageProvider.__init__(self, img_type)

    def requestPixmap(self, id, size):    
        width = 480
        height = 320
        
        if size.width() > 0:
            width = size.width()
        if size.height() > 0:
            height = size.height()
    
        size = QSize(width, height)
        
        def create_image(width, height):
            dpi = self._fig.get_dpi()
            self._fig.set_size_inches((width/dpi, height/dpi))
            self._fig.canvas.draw()
            width, height = self._fig.canvas.get_width_height()
            img = self._fig.canvas.tostring_rgb()
            img = np.fromstring(img, dtype=np.uint8).reshape(height, width, 3)
            return img            
        
        img = create_image(size.width(), size.height())
        width, height = img.shape[:2]        
                
        qimg = QImage(img, height, width, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        
        return pixmap, size
        
        
def main():
    app = QGuiApplication(sys.argv)
    
    engine = QQmlApplicationEngine(parent=app)
    
    context = engine.rootContext()
    data_model = DataSeriesModel()
    context.setContextProperty("dataModel", data_model)
    mainApp = Form(data_model)
    # mainApp = Form()
    context.setContextProperty("draw_mpl", mainApp)
    
    engine.addImageProvider("mplFigure", MatplotlibImageProvider(mainApp.figure))
    engine.load(QUrl('main.qml'))
    
    rc = app.exec_()
    sys.exit(rc)


if __name__ == "__main__":
    main()