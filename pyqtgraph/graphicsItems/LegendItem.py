from .GraphicsWidget import GraphicsWidget
from .LabelItem import LabelItem
from ..Qt import QtGui, QtCore
from .. import functions as fn
from ..Point import Point
from .ScatterPlotItem import ScatterPlotItem, drawSymbol
from .PlotDataItem import PlotDataItem
from .GraphicsWidgetAnchor import GraphicsWidgetAnchor
__all__ = ['LegendItem']


class LegendItem(GraphicsWidget, GraphicsWidgetAnchor):
    """
    Displays a legend used for describing the contents of a plot.
    LegendItems are most commonly created by calling PlotItem.addLegend().

    Note that this item should not be added directly to a PlotItem. Instead,
    Make it a direct descendant of the PlotItem::

        legend.setParentItem(plotItem)

    """
    def __init__(self, size=None, offset=None, pen=None, brush=None, textSize=None, 
                 textBold=None, textItalic=None, sampleScale=1):
        """
        ==============  ===============================================================
        **Arguments:**
        size            Specifies the fixed size (width, height) of the legend. If
                        this argument is omitted, the legend will automatically resize
                        to fit its contents.
        offset          Specifies the offset position relative to the legend's parent.
                        Positive values offset from the left or top; negative values
                        offset from the right or bottom. If offset is None, the
                        legend must be anchored manually by calling anchor() or
                        positioned by calling setPos().
        horSpacing      Specifies the spacing between the line symbol and the label.
        verSpacing      Specifies the spacing between individual entries of the legend
                        vertically. (Can also be negative to have them really close)
        pen             Pen to use when drawing legend border. Any single argument
                        accepted by :func:`mkPen <pyqtgraph.mkPen>` is allowed.
        brush           QBrush to use as legend background filling. Any single argument
                        accepted by :func:`mkBrush <pyqtgraph.mkBrush>` is allowed.
        labelTextColor  Pen to use when drawing legend text. Any single argument
                        accepted by :func:`mkPen <pyqtgraph.mkPen>` is allowed.
        ==============  ===============================================================

        """


        GraphicsWidget.__init__(self)
        GraphicsWidgetAnchor.__init__(self)
        self.setFlag(self.ItemIgnoresTransformations)
        self.layout = QtGui.QGraphicsGridLayout()
        self.layout.setVerticalSpacing(verSpacing)
        self.layout.setHorizontalSpacing(horSpacing)

        self.setLayout(self.layout)
        self.items = []
        self.size = size
        if size is not None:
            self.setGeometry(QtCore.QRectF(0, 0, self.size[0], self.size[1]))

        
        self.pen = pen if pen else fn.mkPen(255,255,255,100) 
        self.brush = brush if brush else fn.mkBrush(100,100,100,50)

        self.labelOptions = dict(size=textSize, bold=textBold, italic=textItalic, sampleScale=sampleScale)
        self.labelOptions = {k:v for k, v in self.labelOptions.items() if v is not None}
        
    def setParentItem(self, p):
        ret = GraphicsWidget.setParentItem(self, p)
        if self.offset is not None:
            offset = Point(self.opts['offset'])
            anchorx = 1 if offset[0] <= 0 else 0
            anchory = 1 if offset[1] <= 0 else 0
            anchor = (anchorx, anchory)
            self.anchor(itemPos=anchor, parentPos=anchor, offset=offset)
        return ret
        
    def addItem(self, item, name, **kwargs):
        """
        Add a new entry to the legend.

        ==============  ========================================================
        **Arguments:**
        item            A PlotDataItem from which the line and point style
                        of the item will be determined or an instance of
                        ItemSample (or a subclass), allowing the item display
                        to be customized.
        title           The title to display for this item. Simple HTML allowed.
        ==============  ========================================================
        """
        opts = self.labelOptions.copy()
        opts.update(kwargs)
        label = LabelItem(name, **opts)
        if isinstance(item, ItemSample):
            sample = item
        else:
            sample = ItemSample(item, sampleScale=opts['sampleScale'])
        row = self.layout.rowCount()
        self.items.append((sample, label))
        self.layout.addItem(sample, row, 0)
        self.layout.addItem(label, row, 1)
        self.updateSize()

    def removeItem(self, item):
        """
        Removes one item from the legend.

        ==============  ========================================================
        **Arguments:**
        item            The item to remove or its name.
        ==============  ========================================================
        """
        for sample, label in self.items:
            if sample.item is item or label.text == item:
                self.items.remove((sample, label))      # remove from itemlist
                self.layout.removeItem(sample)          # remove from layout
                sample.close()                          # remove from drawing
                self.layout.removeItem(label)
                label.close()
                self.updateSize()                       # redraq box
                return                                  # return after first match

    def clear(self):
        """Removes all items from legend."""
        for sample, label in self.items:
            self.layout.removeItem(sample)
            self.layout.removeItem(label)

        self.items = []
        self.updateSize()

    def clear(self):
        """
        Removes all items from the legend.

        Useful for reusing and dynamically updating charts and their legends.
        """
        while self.items != []:
            self.removeItem(self.items[0][1].text)
                
    def updateSize(self):
        if self.size is not None:
            return

        self.setGeometry(0, 0, 0, 0)

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.width(), self.height())

    def paint(self, p, *args):
        p.setPen(self.pen)
        p.setBrush(self.brush)
        p.drawRect(self.boundingRect())

    def hoverEvent(self, ev):
        ev.acceptDrags(QtCore.Qt.LeftButton)

    def mouseDragEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            ev.accept()
            dpos = ev.pos() - ev.lastPos()
            self.autoAnchor(self.pos() + dpos)
    
    def setTextSize(self, size):
        self.setTextOption(size=size)

    def setTextOption(self, **opts):
        for k, v in opts.items():
            if k.lower() == "size" and isinstance(v, int):
                v = str(v) + "pt"
            self.labelOptions[k] = v

    def setTextBold(self, bold):
        self.lableOptions["bold"] = bold
  
    def setTextItalic(self, italic):
        self.lableOptions["italic"] = italic

    def setPen(self, pen):
        self.pen = fn.mkPen(pen)

    def setBrush(self, brush):
        self.brush = fn.mkBrush(brush)
        
    def setOpacity(self, level):
        color = self.brush.color()
        color.setAlpha(level)
        self.brush.setColor(color)
        
class ItemSample(GraphicsWidget):
    """ Class responsible for drawing a single item in a LegendItem (sans label).

    This may be subclassed to draw custom graphics in a Legend.
    """
    ## Todo: make this more generic; let each item decide how it should be represented.
    def __init__(self, item, sampleScale=1):
        GraphicsWidget.__init__(self)
        self.item = item
        self.sampleScale = sampleScale
    
    def boundingRect(self):
        return QtCore.QRectF(0, 0, 20, 20)

    def paint(self, p, *args):
        opts = self.item.opts

        if opts['antialias']:
            p.setRenderHint(p.Antialiasing)

        if not isinstance(self.item, ScatterPlotItem):
            pen = opts['pen']
            if isinstance(pen, QtGui.QPen):
                newpen = fn.mkPen(pen, width=pen.width() * self.sampleScale)
            else:
                newpen = fn.mkPen(pen, width=self.sampleScale)
            p.setPen(newpen)
            p.drawLine(2, 18, 18, 2)
        
        symbol = opts.get('symbol', None)
        if symbol is not None:
            if isinstance(self.item, PlotDataItem):
                opts = self.item.scatter.opts

            pen = fn.mkPen(opts['pen'])
            brush = fn.mkBrush(opts['brush'])
            size = opts['size']

            p.translate(10, 10)
            path = drawSymbol(p, symbol, size, pen, brush)




