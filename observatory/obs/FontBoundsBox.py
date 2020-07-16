from mojo.UI import *
from mojo.events import addObserver, removeObserver
from mojo.drawingTools import *
from vanilla import *
from lib.tools.defaults import getDefault, setDefault
from lib.tools.notifications import PostNotification
from mojo.extensions import getExtensionDefault, setExtensionDefault, getExtensionDefaultColor, setExtensionDefaultColor
from random import choice
from mojo.roboFont import CurrentFont
from AppKit import NSImageNameRefreshTemplate, NSColor
from lib.UI.toggleImageButton import ToggleImageButton

title = "Font Bounding Box"  # Keep them unique!
event = "drawBackground"

turnOffItems = []

settingsWindow = "%sSettingsKey" % title


# dont edit
selfKey = "%sKey" % title
wasOn = getExtensionDefault(selfKey)
# dont change name of class


class ThisObserver(object):

    def __init__(self, active=bool):
        self.ufo = None
        self.active = active
        if getExtensionDefault(selfKey):
            if self.active == True:
                return
            if self.active == False:
                pass

        if self.active == True:
            self._activate()
            self.turnOff()
        if self.active == False:
            self._end()
        self.load()

    # dont change names of functions
    # dont edit _functions!
    # but you can add functions if needed

    def load(self):
        pass

    def _activate(self):
        setExtensionDefault(selfKey, self)
        addObserver(self, "mainFunction", event)
        # Add more if you need
        self.calculateBoundingBox()  # init calc bounds

    def _end(self):
        removeObserver(getExtensionDefault(selfKey), event)
        # See _activate()

        setExtensionDefault(selfKey, None)
        # this is optional
        if wasOn:
            self.restoreGlyphViewItems()
        # kill settings window
        self.settingsWindow(onOff=False)

    def mainFunction(self, info):
        if not getExtensionDefault(settingsWindow):
            self.settingsWindow(onOff=True)
        save()
        stroke(0.01, 0.68, 0.5, 1)
        strokeWidth(1)
        fill(None)
        rect(self.xmin[0], self.ymin[0], self.xmax[0] -
             self.xmin[0], self.ymax[0]-self.ymin[0])

        restore()

    def settingsWindow(self, onOff=bool):
        if onOff == True:

            self.w = FloatingWindow((220, 175), "FBB", closable=False)

            setExtensionDefault(settingsWindow, self.w)  # dont change

            self.w.knop = Button((7, 7, -7, 23), "Calculate",
                                 callback=self.calculateBoundingBox)

            # t = """x-  %s\ny-  %s\nx+  %s\ny+  %s""" % (
            # self.xmin[1], self.ymin[1], self.xmax[1], self.ymax[1])
            # self.w.r = TextBox((7, 30, -7, -7), t)

            columnDescriptions = [
                dict(title="B", width=20),
                dict(title="glyphname", editable=False),
                dict(title="value", width=60, editable=False),
            ]
            self.w.results = List((0, 35, -0, -0),
                                  items=[
                                      {"B": 'a', "glyphname": ".notdef", "value": 150}],
                                  columnDescriptions=columnDescriptions,
                                  doubleClickCallback=self.doubleClickCallback
                                  )

            self.w.open()

        # dont change here
        if onOff == False:
            try:
                getExtensionDefault(settingsWindow).hide()
                setExtensionDefault(settingsWindow, None)
            except:
                pass

    def doubleClickCallback(self, sender):
        currentList = sender.get()
        selection = sender.getSelection()[0]
        glyph = currentList[selection]['glyphname']
        SetCurrentGlyphByName(glyph)

    def calculateBoundingBox(self, sender=None):
        xmin = [9999, ""]
        ymin = [9999, ""]
        xmax = [-9999, ""]
        ymax = [-9999, ""]

        for g in CurrentFont():
            if g.bounds:
                if xmin[0] > g.bounds[0]:
                    xmin[0] = g.bounds[0]
                    xmin[1] = g.name
                if ymin[0] > g.bounds[1]:
                    ymin[0] = g.bounds[1]
                    ymin[1] = g.name
                if xmax[0] < g.bounds[2]:
                    xmax[0] = g.bounds[2]
                    xmax[1] = g.name
                if ymax[0] < g.bounds[3]:
                    ymax[0] = g.bounds[3]
                    ymax[1] = g.name
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        PostNotification('doodle.updateGlyphView')
        if hasattr(self, 'w'):
            l = []
            # if hasattr(self, 'w'):
            l.append(dict(B='←', glyphname=xmin[1], value=xmin[0]))
            l.append(dict(B='↓', glyphname=ymin[1], value=ymin[0]))
            l.append(dict(B='→', glyphname=xmax[1], value=xmax[0]))
            l.append(dict(B='↑', glyphname=ymax[1], value=ymax[0]))
            l.append(dict(B='↔︎', glyphname="full width",
                          value=self.xmax[0]-self.xmin[0]))
            l.append(dict(B='↕︎', glyphname="full height",
                          value=self.ymax[0]-self.ymin[0]))
            # {"B": 'a', "glyphname": self.xmin[1], "value": str(
            #     self.xmin[0])}

            self.w.results.set(l)

    def updateView(self, sender):
        PostNotification('doodle.updateGlyphView')

    def turnOff(self):
        pref_as_is = getDefault('glyphZoomViewShowItems')
        pref_new = dict()
        for i in pref_as_is:
            if i in turnOffItems:
                # global gridWasOn
                # gridWasOn = pref_as_is[i]
                pref_new[i] = 0
            else:
                pref_new[i] = pref_as_is[i]
        setDefault('glyphZoomViewShowItems', pref_new)
        PostNotification("doodle.preferencesChanged")

    def restoreGlyphViewItems(self):
        pref_as_is = getDefault('glyphZoomViewShowItems')
        pref_new = dict()
        for i in pref_as_is:
            if i in turnOffItems:
                # global gridWasOn
                # gridWasOn = pref_as_is[i]
                pref_new[i] = 1
            else:
                pref_new[i] = pref_as_is[i]
        setDefault('glyphZoomViewShowItems', pref_new)
        PostNotification("doodle.preferencesChanged")
