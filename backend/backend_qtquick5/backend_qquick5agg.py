import ctypes 
import os
import sys
import traceback    

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from matplotlib.externals import six

from PyQt5 import QtCore, QtGui, QtQuick

DEBUG = True

class MatplotlibIconProvider(QtQuick.QQuickImageProvider):

    def __init__(self, img_type = QtQuick.QQuickImageProvider.Pixmap):
        self.basedir = os.path.join(matplotlib.rcParams['datapath'], 'images')
        QtQuick.QQuickImageProvider.__init__(self, img_type)

    def requestImage(self, id, size):
        img = QtGui.QImage(os.path.join(self.basedir, id + '.svg'))
        size = img.size()
        return img, size
        
    def requestPixmap(self, id, size):    
        img, size = self.requestImage(id, size)
        pixmap = QtGui.QPixmap.fromImage(img)
        
        return pixmap, size

class FigureCanvasQtQuickAgg(QtQuick.QQuickPaintedItem, FigureCanvasAgg):
    # map Qt button codes to MouseEvent's ones:
    buttond = {QtCore.Qt.LeftButton: 1,
               QtCore.Qt.MidButton: 2,
               QtCore.Qt.RightButton: 3,
               # QtCore.Qt.XButton1: None,
               # QtCore.Qt.XButton2: None,
               }

    def __init__(self, figure, parent=None, coordinates=True):
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
        
        # TODO need maybe to use self.grabMouse() of QQuickItem to emulate
        # the same effect
        # self.setMouseTracking(True)
        
        self._agg_draw_pending = False
        
        #
        # Attributes from NavigationToolbar2QT
        #
        # self.coordinates = coordinates
        # self._actions = {}
        #
        # Attributes from NavigationToolbar2
        #
        self.canvas = self.figure.canvas
        self.toolbar = self
        # # a dict from axes index to a list of view limits
        # self._views = matplotlib.cbook.Stack()
        # self._positions = matplotlib.cbook.Stack()  # stack of subplot positions
        # self._xypress = None  # the location and axis info at the time
                              # # of the press
        # self._idPress = None
        # self._idRelease = None
        # self._active = None
        # self._lastCursor = None
        
        # self._idDrag = self.canvas.mpl_connect(
            # 'motion_notify_event', self.mouse_move)

        # self._ids_zoom = []
        # self._zoom_mode = None

        # self._button_pressed = None  # determined by the button pressed
                                     # # at start

        # self.mode = ''  # a mode string for the status bar
        # self.set_history_buttons()

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
        # if the canvas does not have a renderer, then give up and wait for
        # FigureCanvasAgg.draw(self) to be called
        if not hasattr(self, 'renderer'):
            return

        if DEBUG:
            print('FigureCanvasQtQuickAgg.paint: ', self,
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
            
            # if p.isActive():
                # p.end()

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
            
            # if p.isActive():
                # p.end()
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
    
    @QtCore.pyqtProperty('QString', constant=True)
    def defaultDirectory(self):
        startpath = matplotlib.rcParams.get('savefig.directory', '')
        return os.path.expanduser(startpath)
    
    @QtCore.pyqtProperty('QStringList', constant=True)
    def fileFilters(self):
        filetypes = self.canvas.get_supported_filetypes_grouped()
        sorted_filetypes = list(six.iteritems(filetypes))
        sorted_filetypes.sort()
        
        filters = []
        for name, exts in sorted_filetypes:
            exts_list = " ".join(['*.%s' % ext for ext in exts])
            filter = '%s (%s)' % (name, exts_list)
            filters.append(filter)
        
        return filters

    @QtCore.pyqtProperty('QString', constant=True)
    def defaultFileFilter(self):        
        default_filetype = self.canvas.get_default_filetype()
        
        selectedFilter = None
        for filter in self.fileFilters:
            exts = filter.split('(', maxsplit=1)[1]
            exts = exts[:-1].split()
            if default_filetype in exts:
                selectedFilter = filter
                break
        
        if selectedFilter is None:
            selectedFilter = self.fileFilters[0]
                
        return selectedFilter
    
    @QtCore.pyqtSlot(str)
    def print_figure(self, fname, *args, **kwargs):
        if fname:
            fname = QtCore.QUrl(fname).toLocalFile()
            # save dir for next time
            savefig_dir = os.path.dirname(six.text_type(fname))
            matplotlib.rcParams['savefig.directory'] = savefig_dir
            fname = six.text_type(fname)
        FigureCanvasAgg.print_figure(self, fname, *args, **kwargs)
        self.draw()
        
    def hoverEnterEvent(self, event):
        FigureCanvasAgg.enter_notify_event(self, guiEvent=event)

    def hoverLeaveEvent(self, event):
        QtGui.QApplication.restoreOverrideCursor()
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

    # def resizeEvent(self, event):
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

            key = six.unichr(event_key)
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
    
    #
    # Navigation actions from NavigationToolbar2
    #
    # def set_message(self, s):
        # """Display a message on toolbar or in status bar"""
        # self.message.emit(s)
        # if self.coordinates:
            # self.locLabel.setText(s)

    # @QtCore.pyqtSlot()
    # def back(self, *args):
        # """move back up the view lim stack"""
        # self._views.back()
        # self._positions.back()
        # self.set_history_buttons()
        # self._update_view()

    # def dynamic_update(self):
        # self.canvas.draw_idle()

    # def draw_rubberband(self, event, x0, y0, x1, y1):
        # """Draw a rectangle rubberband to indicate zoom limits"""
        # height = self.canvas.figure.bbox.height
        # y1 = height - y1
        # y0 = height - y0

        # w = abs(x1 - x0)
        # h = abs(y1 - y0)

        # rect = [int(val)for val in (min(x0, x1), min(y0, y1), w, h)]
        # self.canvas.drawRectangle(rect)

    # def remove_rubberband(self):
        # """Remove the rubberband"""
        # self.canvas.drawRectangle(None)

    # # def configure_subplots(self):
        # # image = os.path.join(matplotlib.rcParams['datapath'],
                             # # 'images', 'matplotlib.png')
        # # dia = SubplotToolQt(self.canvas.figure, self.parent)
        # # dia.setWindowIcon(QtGui.QIcon(image))
        # # dia.exec_()

    # @QtCore.pyqtSlot()
    # def forward(self, *args):
        # """Move forward in the view lim stack"""
        # self._views.forward()
        # self._positions.forward()
        # self.set_history_buttons()
        # self._update_view()

    # @QtCore.pyqtSlot()
    # def home(self, *args):
        # """Restore the original view"""
        # self._views.home()
        # self._positions.home()
        # self.set_history_buttons()
        # self._update_view()

    # # def _init_toolbar(self):
        # # """
        # # This is where you actually build the GUI widgets (called by
        # # __init__).  The icons ``home.xpm``, ``back.xpm``, ``forward.xpm``,
        # # ``hand.xpm``, ``zoom_to_rect.xpm`` and ``filesave.xpm`` are standard
        # # across backends (there are ppm versions in CVS also).

        # # You just need to set the callbacks

        # # home         : self.home
        # # back         : self.back
        # # forward      : self.forward
        # # hand         : self.pan
        # # zoom_to_rect : self.zoom
        # # filesave     : self.save_figure

        # # You only need to define the last one - the others are in the base
        # # class implementation.

        # # """
        # # raise NotImplementedError

    # def _set_cursor(self, event):
        # if not event.inaxes or not self._active:
            # if self._lastCursor != cursors.POINTER:
                # self.set_cursor(cursors.POINTER)
                # self._lastCursor = cursors.POINTER
        # else:
            # if self._active == 'ZOOM':
                # if self._lastCursor != cursors.SELECT_REGION:
                    # self.set_cursor(cursors.SELECT_REGION)
                    # self._lastCursor = cursors.SELECT_REGION
            # elif (self._active == 'PAN' and
                  # self._lastCursor != cursors.MOVE):
                # self.set_cursor(cursors.MOVE)

                # self._lastCursor = cursors.MOVE

    # def mouse_move(self, event):
        # self._set_cursor(event)

        # if event.inaxes and event.inaxes.get_navigate():

            # try:
                # s = event.inaxes.format_coord(event.xdata, event.ydata)
            # except (ValueError, OverflowError):
                # pass
            # else:
                # artists = [a for a in event.inaxes.mouseover_set
                           # if a.contains(event)]

                # if artists:

                    # a = max(enumerate(artists), key=lambda x: x[1].zorder)[1]
                    # if a is not event.inaxes.patch:
                        # data = a.get_cursor_data(event)
                        # if data is not None:
                            # s += ' [%s]' % a.format_cursor_data(data)

                # if len(self.mode):
                    # self.set_message('%s, %s' % (self.mode, s))
                # else:
                    # self.set_message(s)
        # else:
            # self.set_message(self.mode)

    # @QtCore.pyqtSlot()
    # def pan(self, *args):
        # """Activate the pan/zoom tool. pan with left button, zoom with right"""
        # # set the pointer icon and button press funcs to the
        # # appropriate callbacks

        # if self._active == 'PAN':
            # self._active = None
        # else:
            # self._active = 'PAN'
        # if self._idPress is not None:
            # self._idPress = self.canvas.mpl_disconnect(self._idPress)
            # self.mode = ''

        # if self._idRelease is not None:
            # self._idRelease = self.canvas.mpl_disconnect(self._idRelease)
            # self.mode = ''

        # if self._active:
            # self._idPress = self.canvas.mpl_connect(
                # 'button_press_event', self.press_pan)
            # self._idRelease = self.canvas.mpl_connect(
                # 'button_release_event', self.release_pan)
            # self.mode = 'pan/zoom'
            # self.canvas.widgetlock(self)
        # else:
            # self.canvas.widgetlock.release(self)

        # for a in self.canvas.figure.get_axes():
            # a.set_navigate_mode(self._active)

        # self.set_message(self.mode)

    # def press(self, event):
        # """Called whenver a mouse button is pressed."""
        # pass

    # def press_pan(self, event):
        # """the press mouse button in pan/zoom mode callback"""

        # if event.button == 1:
            # self._button_pressed = 1
        # elif event.button == 3:
            # self._button_pressed = 3
        # else:
            # self._button_pressed = None
            # return

        # x, y = event.x, event.y

        # # push the current view to define home if stack is empty
        # if self._views.empty():
            # self.push_current()

        # self._xypress = []
        # for i, a in enumerate(self.canvas.figure.get_axes()):
            # if (x is not None and y is not None and a.in_axes(event) and
                    # a.get_navigate() and a.can_pan()):
                # a.start_pan(x, y, event.button)
                # self._xypress.append((a, i))
                # self.canvas.mpl_disconnect(self._idDrag)
                # self._idDrag = self.canvas.mpl_connect('motion_notify_event',
                                                       # self.drag_pan)

        # self.press(event)

    # def press_zoom(self, event):
        # """the press mouse button in zoom to rect mode callback"""
        # # If we're already in the middle of a zoom, pressing another
        # # button works to "cancel"
        # if self._ids_zoom != []:
            # for zoom_id in self._ids_zoom:
                # self.canvas.mpl_disconnect(zoom_id)
            # self.release(event)
            # self.draw()
            # self._xypress = None
            # self._button_pressed = None
            # self._ids_zoom = []
            # return

        # if event.button == 1:
            # self._button_pressed = 1
        # elif event.button == 3:
            # self._button_pressed = 3
        # else:
            # self._button_pressed = None
            # return

        # x, y = event.x, event.y

        # # push the current view to define home if stack is empty
        # if self._views.empty():
            # self.push_current()

        # self._xypress = []
        # for i, a in enumerate(self.canvas.figure.get_axes()):
            # if (x is not None and y is not None and a.in_axes(event) and
                    # a.get_navigate() and a.can_zoom()):
                # self._xypress.append((x, y, a, i, a._get_view()))

        # id1 = self.canvas.mpl_connect('motion_notify_event', self.drag_zoom)
        # id2 = self.canvas.mpl_connect('key_press_event',
                                      # self._switch_on_zoom_mode)
        # id3 = self.canvas.mpl_connect('key_release_event',
                                      # self._switch_off_zoom_mode)

        # self._ids_zoom = id1, id2, id3
        # self._zoom_mode = event.key

        # self.press(event)

    # def _switch_on_zoom_mode(self, event):
        # self._zoom_mode = event.key
        # self.mouse_move(event)

    # def _switch_off_zoom_mode(self, event):
        # self._zoom_mode = None
        # self.mouse_move(event)

    # def push_current(self):
        # """push the current view limits and position onto the stack"""
        # views = []
        # pos = []
        # for a in self.canvas.figure.get_axes():
            # views.append(a._get_view())
            # # Store both the original and modified positions
            # pos.append((
                # a.get_position(True).frozen(),
                # a.get_position().frozen()))
        # self._views.push(views)
        # self._positions.push(pos)
        # self.set_history_buttons()

    # def release(self, event):
        # """this will be called whenever mouse button is released"""
        # pass

    # def release_pan(self, event):
        # """the release mouse button callback in pan/zoom mode"""

        # if self._button_pressed is None:
            # return
        # self.canvas.mpl_disconnect(self._idDrag)
        # self._idDrag = self.canvas.mpl_connect(
            # 'motion_notify_event', self.mouse_move)
        # for a, ind in self._xypress:
            # a.end_pan()
        # if not self._xypress:
            # return
        # self._xypress = []
        # self._button_pressed = None
        # self.push_current()
        # self.release(event)
        # self.draw()

    # def drag_pan(self, event):
        # """the drag callback in pan/zoom mode"""

        # for a, ind in self._xypress:
            # #safer to use the recorded button at the press than current button:
            # #multiple button can get pressed during motion...
            # a.drag_pan(self._button_pressed, event.key, event.x, event.y)
        # self.dynamic_update()

    # def drag_zoom(self, event):
        # """the drag callback in zoom mode"""

        # if self._xypress:
            # x, y = event.x, event.y
            # lastx, lasty, a, ind, view = self._xypress[0]

            # # adjust x, last, y, last
            # x1, y1, x2, y2 = a.bbox.extents
            # x, lastx = max(min(x, lastx), x1), min(max(x, lastx), x2)
            # y, lasty = max(min(y, lasty), y1), min(max(y, lasty), y2)

            # if self._zoom_mode == "x":
                # x1, y1, x2, y2 = a.bbox.extents
                # y, lasty = y1, y2
            # elif self._zoom_mode == "y":
                # x1, y1, x2, y2 = a.bbox.extents
                # x, lastx = x1, x2

            # self.draw_rubberband(event, x, y, lastx, lasty)

    # def release_zoom(self, event):
        # """the release mouse button callback in zoom to rect mode"""
        # for zoom_id in self._ids_zoom:
            # self.canvas.mpl_disconnect(zoom_id)
        # self._ids_zoom = []

        # self.remove_rubberband()

        # if not self._xypress:
            # return

        # last_a = []

        # for cur_xypress in self._xypress:
            # x, y = event.x, event.y
            # lastx, lasty, a, ind, view = cur_xypress
            # # ignore singular clicks - 5 pixels is a threshold
            # # allows the user to "cancel" a zoom action
            # # by zooming by less than 5 pixels
            # if ((abs(x - lastx) < 5 and self._zoom_mode!="y") or
                    # (abs(y - lasty) < 5 and self._zoom_mode!="x")):
                # self._xypress = None
                # self.release(event)
                # self.draw()
                # return

            # # detect twinx,y axes and avoid double zooming
            # twinx, twiny = False, False
            # if last_a:
                # for la in last_a:
                    # if a.get_shared_x_axes().joined(a, la):
                        # twinx = True
                    # if a.get_shared_y_axes().joined(a, la):
                        # twiny = True
            # last_a.append(a)

            # if self._button_pressed == 1:
                # direction = 'in'
            # elif self._button_pressed == 3:
                # direction = 'out'
            # else:
                # continue

            # a._set_view_from_bbox((lastx, lasty, x, y), direction,
                                  # self._zoom_mode, twinx, twiny)

        # self.draw()
        # self._xypress = None
        # self._button_pressed = None

        # self._zoom_mode = None

        # self.push_current()
        # self.release(event)

    # # # Probably never used
    # # def draw(self):
        # # """Redraw the canvases, update the locators"""
        # # for a in self.canvas.figure.get_axes():
            # # xaxis = getattr(a, 'xaxis', None)
            # # yaxis = getattr(a, 'yaxis', None)
            # # locators = []
            # # if xaxis is not None:
                # # locators.append(xaxis.get_major_locator())
                # # locators.append(xaxis.get_minor_locator())
            # # if yaxis is not None:
                # # locators.append(yaxis.get_major_locator())
                # # locators.append(yaxis.get_minor_locator())

            # # for loc in locators:
                # # loc.refresh()
        # # self.canvas.draw_idle()

    # def _update_view(self):
        # """Update the viewlim and position from the view and
        # position stack for each axes
        # """

        # views = self._views()
        # if views is None:
            # return
        # pos = self._positions()
        # if pos is None:
            # return
        # for i, a in enumerate(self.canvas.figure.get_axes()):
            # a._set_view(views[i])
            # # Restore both the original and modified positions
            # a.set_position(pos[i][0], 'original')
            # a.set_position(pos[i][1], 'active')

        # self.canvas.draw_idle()

    # def set_cursor(self, cursor):
        # """
        # Set the current cursor to one of the :class:`Cursors`
        # enums values
        # """
        # if DEBUG:
            # print('Set cursor', cursor)
        # self.canvas.setCursor(cursord[cursor])

    # def update(self):
        # """Reset the axes stack"""
        # self._views.clear()
        # self._positions.clear()
        # self.set_history_buttons()

    # @QtCore.pyqtSlot()
    # def zoom(self, *args):
        # """Activate zoom to rect mode"""
        # if self._active == 'ZOOM':
            # self._active = None
        # else:
            # self._active = 'ZOOM'

        # if self._idPress is not None:
            # self._idPress = self.canvas.mpl_disconnect(self._idPress)
            # self.mode = ''

        # if self._idRelease is not None:
            # self._idRelease = self.canvas.mpl_disconnect(self._idRelease)
            # self.mode = ''

        # if self._active:
            # self._idPress = self.canvas.mpl_connect('button_press_event',
                                                    # self.press_zoom)
            # self._idRelease = self.canvas.mpl_connect('button_release_event',
                                                      # self.release_zoom)
            # self.mode = 'zoom rect'
            # self.canvas.widgetlock(self)
        # else:
            # self.canvas.widgetlock.release(self)

        # for a in self.canvas.figure.get_axes():
            # a.set_navigate_mode(self._active)

        # self.set_message(self.mode)

    # def set_history_buttons(self):
        # """Enable or disable back/forward button"""
        # pass
        
FigureCanvasQTAgg = FigureCanvasQtQuickAgg