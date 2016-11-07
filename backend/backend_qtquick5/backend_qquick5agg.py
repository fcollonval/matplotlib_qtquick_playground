from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys                        
                        
from matplotlib.backends.backend_agg import FigureCanvasAgg

from matplotlib.figure import Figure

from matplotlib.externals import six

from PyQt5 import QtCore, QtGui, QtQuick

DEBUG = True

class FigureCanvasQtQuickAgg(QtQuick.QQuickPaintedItem, FigureCanvasAgg):

    #
    # The paint() function taking care of the painting operation is
    # defined in the FigureCanvasQTAggBase
    # This class implement the xyzEvent protected function of QQuickItem
    # 

    # map Qt button codes to MouseEvent's ones:
    buttond = {QtCore.Qt.LeftButton: 1,
               QtCore.Qt.MidButton: 2,
               QtCore.Qt.RightButton: 3,
               # QtCore.Qt.XButton1: None,
               # QtCore.Qt.XButton2: None,
               }

    def __init__(self, figure, parent=None):
        if DEBUG:
            print('FigureCanvasQtQuickAgg qtquick5: ', figure)
        # _create_qApp()
        if figure is None:
            figure = Figure((6.0, 4.0))

        # NB: Using super for this call to avoid a TypeError:
        # __init__() takes exactly 2 arguments (1 given) on QWidget
        # PyQt5
        # The need for this change is documented here
        # http://pyqt.sourceforge.net/Docs/PyQt5/pyqt4_differences.html#cooperative-multi-inheritance
        # super(FigureCanvasQtQuickAgg, self).__init__(figure=figure, parent=parent)
        QtQuick.QQuickPaintedItem.__init__(self, parent=parent)
        FigureCanvasAgg.__init__(self, figure=figure)

        self._drawRect = None
        self.blitbox = None
        
        # self.figure = figure
        print(self.figure)
        
        # TODO need maybe to use self.grabMouse() of QQuickItem to emulate
        # the same effect
        # self.setMouseTracking(True)
        
        # TODO synchronize canvas size
        # self.resize(self.width(), self.height())
        
        self._agg_draw_pending = False

    def getFigure(self):
        return self.figure
        
    def drawRectangle(self, rect):
        self._drawRect = rect
        self.update()

    # def paintEvent(self, e):
    def paint(self, p):
        """
        Copy the image from the Agg canvas to the qt.drawable.
        In Qt, all drawing should be done inside of here when a widget is
        shown onscreen.
        """
        print("paint called")
        # if the canvas does not have a renderer, then give up and wait for
        # FigureCanvasAgg.draw(self) to be called
        if not hasattr(self, 'renderer'):
            return

        if DEBUG:
            print('FigureCanvasQtAgg.paint: ', self,
                  self.get_width_height())

        if self.blitbox is None:
            # matplotlib is in rgba byte order.  QImage wants to put the bytes
            # into argb format and is in a 4 byte unsigned int.  Little endian
            # system is LSB first and expects the bytes in reverse order
            # (bgra).
            if QtCore.QSysInfo.ByteOrder == QtCore.QSysInfo.LittleEndian:
                stringBuffer = self.renderer._renderer.tostring_bgra()
            else:
                stringBuffer = self.renderer._renderer.tostring_argb()

            refcnt = sys.getrefcount(stringBuffer)

            # convert the Agg rendered image -> qImage
            qImage = QtGui.QImage(stringBuffer, self.renderer.width,
                                  self.renderer.height,
                                  QtGui.QImage.Format_ARGB32)
            # get the rectangle for the image
            rect = qImage.rect()
            # p = QtGui.QPainter(self)
            # reset the image area of the canvas to be the back-ground color
            p.eraseRect(rect)
            # draw the rendered image on to the canvas
            p.drawPixmap(QtCore.QPoint(0, 0), QtGui.QPixmap.fromImage(qImage))

            # draw the zoom rectangle to the QPainter
            if self._drawRect is not None:
                p.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DotLine))
                x, y, w, h = self._drawRect
                p.drawRect(x, y, w, h)
            
            if p.isActive():
                p.end()

            # This works around a bug in PySide 1.1.2 on Python 3.x,
            # where the reference count of stringBuffer is incremented
            # but never decremented by QImage.
            # TODO: revert PR #1323 once the issue is fixed in PySide.
            del qImage
            if refcnt != sys.getrefcount(stringBuffer):
                _decref(stringBuffer)
        else:
            bbox = self.blitbox
            l, b, r, t = bbox.extents
            w = int(r) - int(l)
            h = int(t) - int(b)
            t = int(b) + h
            reg = self.copy_from_bbox(bbox)
            stringBuffer = reg.to_string_argb()
            qImage = QtGui.QImage(stringBuffer, w, h,
                                  QtGui.QImage.Format_ARGB32)

            pixmap = QtGui.QPixmap.fromImage(qImage)
            p.drawPixmap(QtCore.QPoint(l, self.renderer.height-t), pixmap)

            # draw the zoom rectangle to the QPainter
            if self._drawRect is not None:
                p.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DotLine))
                x, y, w, h = self._drawRect
                p.drawRect(x, y, w, h)
            
            if p.isActive():
                p.end()
            self.blitbox = None

    def draw(self):
        """
        Draw the figure with Agg, and queue a request for a Qt draw.
        """
        # The Agg draw is done here; delaying causes problems with code that
        # uses the result of the draw() to update plot elements.
        FigureCanvasAgg.draw(self)
        self.update()

    def draw_idle(self):
        """
        Queue redraw of the Agg buffer and request Qt paintEvent.
        """
        # The Agg draw needs to be handled by the same thread matplotlib
        # modifies the scene graph from. Post Agg draw request to the
        # current event loop in order to ensure thread affinity and to
        # accumulate multiple draw requests from event handling.
        # TODO: queued signal connection might be safer than singleShot
        if not self._agg_draw_pending:
            self._agg_draw_pending = True
            QtCore.QTimer.singleShot(0, self.__draw_idle_agg)

    def __draw_idle_agg(self, *args):
        if self.height() < 0 or self.width() < 0:
            self._agg_draw_pending = False
            return
        try:
            FigureCanvasAgg.draw(self)
            self.update()
        except Exception:
            # Uncaught exceptions are fatal for PyQt5, so catch them instead.
            traceback.print_exc()
        finally:
            self._agg_draw_pending = False

    def blit(self, bbox=None):
        """
        Blit the region in bbox
        """
        # If bbox is None, blit the entire canvas. Otherwise
        # blit only the area defined by the bbox.
        if bbox is None and self.figure:
            bbox = self.figure.bbox

        self.blitbox = bbox
        l, b, w, h = bbox.bounds
        t = b + h
        self.repaint(l, self.renderer.height-t, w, h)

    def print_figure(self, *args, **kwargs):
        FigureCanvasAgg.print_figure(self, *args, **kwargs)
        self.draw()
        
    def hoverEnterEvent(self, event):
        FigureCanvasAgg.enter_notify_event(self, guiEvent=event)

    def hoverLeaveEvent(self, event):
        QtWidgets.QApplication.restoreOverrideCursor()
        FigureCanvasAgg.leave_notify_event(self, guiEvent=event)

    def mousePressEvent(self, event):
        x = event.pos().x()
        # flipy so y=0 is bottom of canvas
        y = self.figure.bbox.height - event.pos().y()
        button = self.buttond.get(event.button())
        if button is not None:
            FigureCanvasAgg.button_press_event(self, x, y, button,
                                                guiEvent=event)
        if DEBUG:
            print('button pressed:', event.button())

    def mouseDoubleClickEvent(self, event):
        x = event.pos().x()
        # flipy so y=0 is bottom of canvas
        y = self.figure.bbox.height - event.pos().y()
        button = self.buttond.get(event.button())
        if button is not None:
            FigureCanvasAgg.button_press_event(self, x, y,
                                                button, dblclick=True,
                                                guiEvent=event)
        if DEBUG:
            print('button doubleclicked:', event.button())

    def mouseMoveEvent(self, event):
        x = event.x()
        # flipy so y=0 is bottom of canvas
        y = self.figure.bbox.height - event.y()
        FigureCanvasAgg.motion_notify_event(self, x, y, guiEvent=event)
        # if DEBUG: print('mouse move')

    def mouseReleaseEvent(self, event):
        x = event.x()
        # flipy so y=0 is bottom of canvas
        y = self.figure.bbox.height - event.y()
        button = self.buttond.get(event.button())
        if button is not None:
            FigureCanvasAgg.button_release_event(self, x, y, button,
                                                  guiEvent=event)
        if DEBUG:
            print('button released')

    def wheelEvent(self, event):
        x = event.x()
        # flipy so y=0 is bottom of canvas
        y = self.figure.bbox.height - event.y()
        # from QWheelEvent::delta doc
        if event.pixelDelta().x() == 0 and event.pixelDelta().y() == 0:
            steps = event.angleDelta().y() / 120
        else:
            steps = event.pixelDelta().y()

        if steps != 0:
            FigureCanvasAgg.scroll_event(self, x, y, steps, guiEvent=event)
            if DEBUG:
                print('scroll event: delta = %i, '
                      'steps = %i ' % (event.delta(), steps))

    def keyPressEvent(self, event):
        key = self._get_key(event)
        if key is None:
            return
        FigureCanvasAgg.key_press_event(self, key, guiEvent=event)
        if DEBUG:
            print('key press', key)

    def keyReleaseEvent(self, event):
        key = self._get_key(event)
        if key is None:
            return
        FigureCanvasAgg.key_release_event(self, key, guiEvent=event)
        if DEBUG:
            print('key release', key)

    def geometryChanged(self, new_geometry, old_geometry):
        w = new_geometry.width()
        h = new_geometry.height()
        
        if (w <= 0.0) and (h <= 0.0):
            return
            
        if DEBUG:
            print('resize (%d x %d)' % (w, h))
            print("FigureCanvasQtQuickAgg.geometryChanged(%d, %d)" % (w, h))
        dpival = self.figure.dpi
        winch = w / dpival
        hinch = h / dpival
        self.figure.set_size_inches(winch, hinch)
        FigureCanvasAgg.resize_event(self)
        self.draw_idle()
        QtQuick.QQuickPaintedItem.geometryChanged(self, new_geometry, old_geometry)
         
    # def resizeEvent(self, event):
        # w = event.size().width()
        # h = event.size().height()
        # if DEBUG:
            # print('resize (%d x %d)' % (w, h))
            # print("FigureCanvasQt.resizeEvent(%d, %d)" % (w, h))
        # dpival = self.figure.dpi
        # winch = w / dpival
        # hinch = h / dpival
        # self.figure.set_size_inches(winch, hinch)
        # FigureCanvasBase.resize_event(self)
        # self.draw_idle()
        # QtWidgets.QWidget.resizeEvent(self, event)

    # # Absent of QQuickItem
    # def sizeHint(self):
        # w, h = self.get_width_height()
        # return QtCore.QSize(w, h)
        
    # # Absent of QQuickItem
    # def minumumSizeHint(self):
        # return QtCore.QSize(10, 10)

    def _get_key(self, event):
        if event.isAutoRepeat():
            return None

        event_key = event.key()
        event_mods = int(event.modifiers())  # actually a bitmask

        # get names of the pressed modifier keys
        # bit twiddling to pick out modifier keys from event_mods bitmask,
        # if event_key is a MODIFIER, it should not be duplicated in mods
        mods = [name for name, mod_key, qt_key in MODIFIER_KEYS
                if event_key != qt_key and (event_mods & mod_key) == mod_key]
        try:
            # for certain keys (enter, left, backspace, etc) use a word for the
            # key, rather than unicode
            key = SPECIAL_KEYS[event_key]
        except KeyError:
            # unicode defines code points up to 0x0010ffff
            # QT will use Key_Codes larger than that for keyboard keys that are
            # are not unicode characters (like multimedia keys)
            # skip these
            # if you really want them, you should add them to SPECIAL_KEYS
            MAX_UNICODE = 0x10ffff
            if event_key > MAX_UNICODE:
                return None

            key = unichr(event_key)
            # qt delivers capitalized letters.  fix capitalization
            # note that capslock is ignored
            if 'shift' in mods:
                mods.remove('shift')
            else:
                key = key.lower()

        mods.reverse()
        return '+'.join(mods + [key])

    def new_timer(self, *args, **kwargs):
        """
        Creates a new backend-specific subclass of
        :class:`backend_bases.Timer`.  This is useful for getting
        periodic events through the backend's native event
        loop. Implemented only for backends with GUIs.

        optional arguments:

        *interval*
            Timer interval in milliseconds

        *callbacks*
            Sequence of (func, args, kwargs) where func(*args, **kwargs)
            will be executed by the timer every *interval*.

    """
        return TimerQT(*args, **kwargs)

    def flush_events(self):
        global qApp
        qApp.processEvents()

    def start_event_loop(self, timeout):
        FigureCanvasAgg.start_event_loop_default(self, timeout)

    start_event_loop.__doc__ = \
                             FigureCanvasAgg.start_event_loop_default.__doc__

    def stop_event_loop(self):
        FigureCanvasAgg.stop_event_loop_default(self)

    stop_event_loop.__doc__ = FigureCanvasAgg.stop_event_loop_default.__doc__

FigureCanvasQTAgg = FigureCanvasQtQuickAgg