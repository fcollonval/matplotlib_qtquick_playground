"""
Series of data are loaded from a .csv file, and their names are
displayed in a checkable list view. The user can select the series
it wants from the list and plot them on a matplotlib canvas.
Use the sample .csv file that comes with the script for an example
of data series.

[2016-11-06] Convert to QtQuick 2.0 - Qt.labs.controls 1.0
[2016-11-05] Convert to QtQuick 2.0 - QtQuick Controls 1.0
[2016-11-01] Update to PyQt5.6 and python 3.5

Frederic Collonval (fcollonval@gmail.com)

Inspired from the work of Eli Bendersky (eliben@gmail.com):
https://github.com/eliben/code-for-blog/tree/master/2009/pyqt_dataplot_demo

License: MIT License
Last modified: 2016-11-06
"""
import sys, os, csv
from PyQt5.QtCore import Qt, QObject, QUrl
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import qmlRegisterType
from PyQt5.QtQuick import QQuickView

from backend_qtquick5 import FigureCanvasQTAgg

import matplotlib
# matplotlib.use('module://backend_qtquick5')
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
# from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np       
        
def main():
    argv = sys.argv
    
    # Trick to set the style / not found how to do it in pythonic way
    argv.extend(["-style", "universal"])
    app = QGuiApplication(argv)
    
    qmlRegisterType(FigureCanvasQTAgg, "Backend", 1, 0, "FigureCanvas")
    
    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.setSource(QUrl('backend_qtquick5/Figure.qml'))
    view.show()
    
    win = view.rootObject()
    fig = win.findChild(QObject, "figure").getFigure()
    print(fig)
    ax = fig.add_subplot(111)
    x = np.linspace(-5, 5)
    ax.plot(x, np.sin(x))
    
    rc = app.exec_()
    # There is some trouble arising when deleting all the objects here
    # but I have not figure out how to solve the error message.
    # It looks like 'app' is destroyed before some QObject
    sys.exit(rc)


if __name__ == "__main__":
    main()