# coding=utf-8

"""
- load glyphContruction ass dict:
    - compo : accents, anchors
    - accent: base, anchors


TODO:
    updte for the new list sructure


"""

# from _glyphConstructionCategories import *
from glyphConstruction import ParseGlyphConstructionListFromString, GlyphConstructionBuilder

from AppKit import NSColor
from vanilla import *
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.events import addObserver, removeObserver
from mojo.drawingTools import *
from mojo.extensions import getExtensionDefault, setExtensionDefault
from mojo.UI import *
from lib.tools.defaults import getDefault, setDefault
from lib.tools.notifications import PostNotification
from mojo.roboFont import CurrentFont, CurrentGlyph
from fontTools.pens.areaPen import AreaPen

import os
import imp


def loadConstuctions():
    if 'nl.hallotype.glyphConstructions' in CurrentFont().lib:
        construction = CurrentFont().lib['nl.hallotype.glyphConstructions']
    else:
        reloadConstructions()
        construction = CurrentFont().lib['nl.hallotype.glyphConstructions']
    return construction


def isAccent(glyphName):
    if CurrentFont()[glyphName].anchors:
        return CurrentFont()[glyphName].anchors[0].name[0] == "_"

# def makeSuperDict():
#     superdict = sd = {}
#     cs = CurrentFont().lib['nl.hallotype.glyphConstructions']
#     from glyphConstruction import ParseGlyphConstructionListFromString
#     for construction in ParseGlyphConstructionListFromString(cs):
#         compo = construction.split("=")[0][:-1]
#         base = construction.split("=")[1][1:].split("+")[0].strip()
#         accent = construction.split("=")[1][1:].split(
#             "+")[1].strip().split("@")[0]
#         anchor = construction.split("=")[1][1:].split(
#             "+")[1].strip().split("@")[1]

#         if base not in sd:
#             sd[base] = {}
#         if accent not in sd:
#             sd[accent] = {}
#         if anchor not in sd:
#             sd[anchor] = {}
#         if compo not in sd:
#             sd[compo] = {}

#         if base not in sd[accent]:
#             sd[accent][base] = {}
#         if base not in sd[anchor]:
#             sd[anchor][base] = {}
#         if base not in sd[compo]:
#             sd[compo][base] = {}

#         if accent not in sd[base]:
#             sd[base][accent] = {}
#         if accent not in sd[anchor]:
#             sd[anchor][accent] = {}
#         if accent not in sd[compo]:
#             sd[compo][accent] = {}

#         if anchor not in sd[base]:
#             sd[base][anchor] = {}
#         if anchor not in sd[accent]:
#             sd[accent][anchor] = {}
#         if anchor not in sd[compo]:
#             sd[compo][anchor] = {}

#         if compo not in sd[base]:
#             sd[base][compo] = {}
#         if compo not in sd[accent]:
#             sd[accent][compo] = {}
#         if compo not in sd[anchor]:
#             sd[anchor][compo] = {}

#         if anchor not in sd[base][accent]:
#             sd[base][accent][anchor] = compo
#         if accent not in sd[base][anchor]:
#             sd[base][anchor][accent] = compo
#     return sd


#sd = makeSuperDict()

alles = ""
title = "Diacritics"  # Keep them unique!
event = "draw"
turnOffItems = []
turnOnItems = ['Anchors']
settingsWindow = "%sSettingsKey" % title
defaultKey = "nl.hallotype.diacritics"

# dont edit
selfKey = "%sKey" % title
wasOn = getExtensionDefault(selfKey)
pijlen = {
    'top': u'\u2191',
    'bottom': chr(8595),
    'below': chr(8615),
    'right': u"r",
    'middle': u"m",
    'bar': u"–",
    'ogonek': u'˛',
    'cedilla': u'¸',
    'horn': u'h',
    'ring': u'˚',
    'fallbackAnchor': '?'
}

anchorsNames = {
    u'\u2191': 'top',
    chr(8595): 'bottom',
    chr(8615): 'below',
    u"r": 'right',
    u"m": 'middle',
    u"–": 'bar',
    u'o': 'ogonek',
    u'c': 'cedilla',
    u'h': 'horn',
    u'º': 'ring'
}


def makeLookupDicts(myset):
    b = {}
    a = {}
    for construction in myset:
        compo = construction['compo']
        base = construction['base']
        accent = construction['accent']
        anchor = construction['anchor']
        constr = {'accent': accent, 'anchor': anchor}
        b_constr = {'base': base, 'anchor': anchor}

        if base not in b:
            b[base] = {}
            b[base]['accents'] = [accent]
            b[base]['anchors'] = [anchor]
            b[base]['compos'] = [compo]
            b[base]['constructions'] = [constr]

        if accent not in b[base]['accents']:
            b[base]['accents'].append(accent)

        if anchor not in b[base]['anchors']:
            b[base]['anchors'].append(anchor)

        if compo not in b[base]['compos']:
            b[base]['compos'].append(compo)

        if constr not in b[base]['constructions']:
            b[base]['constructions'].append(constr)

        ###
        if accent not in a:
            a[accent] = {}
            a[accent]['bases'] = [base]
            a[accent]['anchors'] = [anchor]
            a[accent]['compos'] = [compo]
            a[accent]['constructions'] = [b_constr]

        if base not in a[accent]['bases']:
            a[accent]['bases'].append(base)

        if anchor not in a[accent]['anchors']:
            a[accent]['anchors'].append(anchor)

        if compo not in a[accent]['compos']:
            a[accent]['compos'].append(compo)

        if b_constr not in a[accent]['constructions']:
            a[accent]['constructions'].append(b_constr)

    return b, a


def anchorInGlyph(anchor, glyph):
    for a in glyph.anchors:
        if a.name == anchor:
            return (True, a.y)
        if a.name == "_"+anchor:
            return (True, a.y)
    return (False, None)


# dont change name of class
class ThisObserver(BaseWindowController):

    def __init__(self, active=bool):
        self.active = active

        self.baseGlyph = None
        self.accent = None
        # self.anchor = None
        self.accentPos = None
        # self.composite = None

        if getExtensionDefault(selfKey):
            if self.active == True:
                return
            if self.active == False:
                pass

        if self.active == True:
            self._activate()
            self._turnOff()
            self._turnOn()
        if self.active == False:
            self._end()

    # dont change names of functions
    # dont edit _functions!
    # but you can add functions if needed

    def _activate(self):
        setExtensionDefault(selfKey, self)
        addObserver(self, "mainFunction", event)
        addObserver(self, "glyphChange", "currentGlyphChanged")
        addObserver(self, "drawPreviewAccents", "drawPreview")
        addObserver(self, "warn", "draw")
        # addObserver(self, "testOverlap", "drawBackground")
        self.reloadConstructions()

    def _end(self):
        removeObserver(getExtensionDefault(selfKey), event)
        removeObserver(getExtensionDefault(selfKey), "currentGlyphChanged")
        removeObserver(getExtensionDefault(selfKey), "drawPreview")
        removeObserver(getExtensionDefault(selfKey), "draw")
        # removeObserver(getExtensionDefault(selfKey), 'drawBackground')

        setExtensionDefault(selfKey, None)
        # this is optional
        if wasOn:
            self._restoreGlyphViewItems()
        # kill settings window
        self.settingsWindow(onOff=False)

    def mainFunction(self, info):
        if not getExtensionDefault(settingsWindow):
            self.settingsWindow(onOff=True)

        self.w = getExtensionDefault(settingsWindow)
        self.drawAccents(info)

    def settingsWindow(self, onOff=bool):
        if onOff == True:
            self.w = FloatingWindow((1443.0, 108.0, 160.0, 72.0),
                                    title, closable=False)
            setExtensionDefault(settingsWindow, self.w)
            # print getExtensionDefault(settingsWindow)
            columnDescriptions = [
                dict(title="", key="checkBox",
                     cell=CheckBoxListCell(), width=15),
                dict(title="accent", editable=False),
                dict(title="anchor", width=50, editable=False),


            ]

            # self.w.latin_supp = SquareButton(
            #     (0, 0, 40, 17), "supp", sizeStyle='mini', callback=self.checkOnUnicode)
            # self.w.latin_A = SquareButton(
            #     (40, 0, 40, 17), "ex a", sizeStyle='mini', callback=self.checkOnUnicode)
            # self.w.latin_B = SquareButton(
            #     (80, 0, 40, 17), "ex b", sizeStyle='mini', callback=self.checkOnUnicode)
            # self.w.latin_add = SquareButton(
            #     (120, 0, 40, 17), "add", sizeStyle='mini', callback=self.checkOnUnicode)

            self.w.allOn = SquareButton(
                (0, 0, 53, 17), "all on", callback=self.allOn, sizeStyle='mini')
            self.w.allOff = SquareButton(
                (53, 0, 53, 17), "all off", callback=self.allOff, sizeStyle='mini')
            self.w.reload = SquareButton(
                (106, 0, -0, 17), "reload", callback=self.reloadConstructions, sizeStyle='mini')
            self.w.list = List((0, 17, -0, -20),
                               items=[],
                               columnDescriptions=columnDescriptions,
                               editCallback=self.listEditCallback,
                               doubleClickCallback=self.goToAccent,
                               )

            self.w.compile = SquareButton(
                (0, -20, -0, -0), 'compile these glyphs', callback=self.compileGlyphs, sizeStyle='small')
            self.setUpBaseWindowBehavior()
            self.w.open()
            self.buildAccentList()

        if onOff == False:
            try:
                getExtensionDefault(settingsWindow).hide()
                setExtensionDefault(settingsWindow, None)
            except:
                pass

    def reloadConstructions(self, sender=None):
        self.construction = loadConstuctions()
        self.baseDict, self.accentDict = makeLookupDicts(self.construction)
        # self.sd = makeSuperDict()
        self.buildAccentList()

    def goToAccent(self, sender):
        currentList = sender.get()
        selection = sender.getSelection()[0]
        accent = currentList[selection]['accent']
        SetCurrentGlyphByName(accent)

    def getGlyphName(self, glyph):
        smallCaps = False
        caps = False
        suffix = ""
        glyphName = glyph.name
        if glyphName == glyph.name.upper():
            caps = True
        if ".sc" in glyph.name:
            glyphName = glyph.name.split(".")[0].upper()
            smallCaps = True
        if ".alt" in glyph.name:
            if smallCaps == False:
                glyphName = glyph.name.split(".")[0]
                suffix = ".%s" % glyph.name.split(".")[1]
            else:
                suffix += ".%s" % glyph.name.split(".")[2]

        return (glyphName, smallCaps, caps, suffix)

    def warn(self, info):
        glyph = CurrentGlyph()
        glyphName = glyph.name
        if glyphName not in self.baseDict.keys():
            return

        glyphAnchors = list()
        for anchor in glyph.anchors:
            glyphAnchors.append(anchor.name)
        missing = list(
            set(self.baseDict[glyphName]['anchors']).difference(set(glyphAnchors)))
        save()
        fill(1, 0, 0, .8)
        stroke(None)
        fontSize(40)
        y = 50
        for a in missing:
            text("missing anchor: %s" % a, (glyph.width+50, y))
            y += 36
        restore()

    def compileGlyphs(self, sender):
        """
        need to rewrite for RF3
        """
        font = CurrentFont()
        g = CurrentGlyph()
        base = g.name
        l = self.w.list.get()
        for i in l:
            if i['checkBox']:
                accent = i['construction']['accent']
                anchor = i['construction']['anchor']
                compo = "testcompo"  # self.sd[base][accent][anchor]
                if base not in font.keys():
                    continue
                if accent not in font.keys():
                    continue

                inBase, height = anchorInGlyph(anchor, font[base])
                if inBase and height > 600:
                    if accent+".cap" in font.keys():
                        accent = accent+".cap"
                inAccent, height = anchorInGlyph(anchor, font[accent])
                construction = "%s = %s + %s@%s" % (compo,
                                                    base, accent, anchor)

                if not inBase:
                    continue
                if not inAccent:
                    continue

                self.compileGlyph(construction)

    def compileGlyph(self, construction):
        font = CurrentFont()
        constructionGlyph = GlyphConstructionBuilder(construction, font)
        glyph = font.newGlyph(constructionGlyph.name, clear=True)
        constructionGlyph.draw(glyph.getPen())
        glyph.name = constructionGlyph.name
        glyph.unicode = constructionGlyph.unicode
        glyph.width = constructionGlyph.width
        glyph.markColor = 1, 1, 0, 0.5
        if glyph.unicode is None:
            glyph.autoUnicodes()

    def allOn(self, sender):
        for i in self.w.list.get():
            i['checkBox'] = True

    def allOff(self, sender):
        for i in self.w.list.get():
            i['checkBox'] = False

    def checkSupp(self, sender):
        pass

    def checkOnUnicode(self, sender):
        if sender == self.w.latin_supp:
            myset = Latin_Supp_block
        if sender == self.w.latin_A:
            myset = Latin_Ext_A_block
        if sender == self.w.latin_B:
            myset = Latin_Ext_B_block
        if sender == self.w.latin_add:
            myset = Latin_Ext_A_block
            myset = Latin_Ext_additional_block

        g = CurrentGlyph()
        defaults = getExtensionDefault(defaultKey, dict())
        # print Latin_Supp_block
        # print
        # print defaults
        # print

        for glyphName in myset:
            if glyphName == g.name:
                # g.name
                for anchorName in myset[glyphName]:
                    # top
                    for accent in myset[glyphName][anchorName]:
                        # grave
                        for listItem in self.w.list.get():

                            for pijl in pijlen.items():
                                if listItem["anchor"] == pijl[1]:
                                    anchor = pijl[0]
                                    if anchor == anchorName and accent == listItem['accent']:
                                        listItem['checkBox'] = True

    def listEditCallback(self, sender):
        # save to defaults
        #defaults = getExtensionDefault(defaultKey, dict())
        # print defaults
        for item in sender:

            # anchor position
            for pijl in pijlen.items():
                if item["anchor"] == pijl[1]:
                    anchor = pijl[0]
            ##

            key = defaultKey+"."+item["accent"]+"@"+anchor
            # print(key)
            value = item["checkBox"]

            setExtensionDefault(key, value)
        UpdateCurrentGlyphView()

    def buildAccentList(self, sender=None):
        self.w = getExtensionDefault(settingsWindow)
        if not self.w:
            return
        font = CurrentFont()
        glyph = CurrentGlyph()

        if glyph is None:
            self.w.setTitle("---")
            self.w.list.set([])
            return

        glyphName = glyph.name
        self.w.setTitle(glyphName)

        if "." in glyphName:
            glyphName = glyphName.split(".")[0]

        theAccentsList = []
        # defaults = getExtensionDefault(defaultKey+".check", dict())
        if glyphName in self.baseDict:
            for accent in self.baseDict[glyphName]['accents']:
                for c in self.baseDict[glyphName]['constructions']:
                    # print(c)
                    if c['accent'] == accent:
                        position = c['anchor']
                        thisConstructon = c
                        if position not in pijlen.keys():
                            pijlen[position] = position

                theAccentsList.append(
                    dict(
                        anchor=pijlen[position],
                        accent=accent,
                        checkBox=getExtensionDefault(
                            defaultKey+"."+accent+"@"+position, True),
                        construction=thisConstructon,
                    ),
                )
        if glyphName in self.accentDict:
            for base in self.accentDict[glyphName]['bases']:
                for c in self.accentDict[glyphName]['constructions']:
                    # print(c)
                    if c['base'] == base:
                        position = c['anchor']
# key = defaultKey+"."+item["accent"]+"@"+anchor
                theAccentsList.append(
                    dict(
                        anchor=pijlen[position],
                        accent=base,
                        checkBox=getExtensionDefault(
                            defaultKey+"."+base+"@"+position, True),
                        construction=self.accentDict[glyphName],
                    ),
                )

        self.w.list.set(theAccentsList)
        # print len(items)
        self.w.resize(160, 17+17+17+17+(19*len(theAccentsList))+21)

    # notifications

    def glyphChange(self, info):
        self.buildAccentList()

    def drawAccents(self, info, preview=False):
        glyph = info["glyph"]
        font = glyph.getParent()

        isAccent = False

        glyphName = glyph.name
        if "." in glyphName:
            glyphName = glyphName.split(".")[0]

        if glyphName in self.accentDict.keys():
            isAccent = True

        # self.baseGlyph = glyph
        # self.accent = None

        # caps = self.getGlyphName(glyph)[2]
        # #print caps
        items = self.w.list.get()

        # save()
        # baseGlyphAnchors = {}
        # for a in glyph.anchors:
        # baseGlyphAnchors[a.name] = [a.x, a.y]

        for item in items:
            if not item["checkBox"]:
                continue
            accent = item['accent']
        #     if caps:
        #         try:
        #             #print accent
        #             if accent+".cap" in font:
        #                 accent = accent + ".cap"
        #         except:
        #             pass

            for pijl in pijlen.items():
                if item["anchor"] == pijl[1]:
                    anchor = pijl[0]

            if accent in font:
                for baseGlyphAnchor in glyph.anchors:
                    # test hier voor cap hoogte
                    if baseGlyphAnchor.y > 550:
                        try:
                            if accent+".cap" in font:
                                accent = accent + ".cap"
                        except:
                            pass

                    for accentAnchor in font[accent].anchors:
                        # zoek hier op welk anchor je moet hebben
                        if accentAnchor.name[1:] == anchor:
                            if accentAnchor.name[1:] == baseGlyphAnchor.name:
                                save()
        #                         # do the transform here
                                x = baseGlyphAnchor.x - accentAnchor.x
                                y = baseGlyphAnchor.y - accentAnchor.y
        #                         # print(baseGlyphAnchor)
                                self.accentPos = (x, y)
                                translate(x, y)
                                fill(0.34, 0.71, 0.14, .7)
                                if preview:
                                    fill(0)
                                stroke(None)

                                drawGlyph(font[accent])
                                self.accent = font[accent]
                                restore()
                        if isAccent:
                            if accentAnchor.name == anchor:
                                if accentAnchor.name == baseGlyphAnchor.name[1:]:
                                    save()
            #                         # do the transform here
                                    x = baseGlyphAnchor.x - accentAnchor.x
                                    y = baseGlyphAnchor.y - accentAnchor.y
            #                         # print(baseGlyphAnchor)
                                    self.accentPos = (x, y)
                                    translate(x, y)
                                    fill(0.34, 0.71, 0.14, .7)
                                    if preview:
                                        fill(0)
                                    stroke(None)

                                    drawGlyph(font[accent])
                                    self.accent = font[accent]
                                    restore()

    def drawPreviewAccents(self, info):
        self.drawAccents(info, True)

    def _turnOn(self):
        pass
        pref_as_is = getDefault('glyphZoomViewShowItems')
        pref_new = dict()
        for i in getDefault('glyphZoomViewShowItems'):
            if i in turnOnItems:
                pref_new[i] = 1
            else:
                pass
        setDefault('glyphZoomViewShowItems', pref_new)
        preferencesChanged()

    def _turnOff(self):
        pref_as_is = getDefault('glyphZoomViewShowItems')
        setExtensionDefault('restoreGlyphZoomViewShowItems', pref_as_is)
        pref_new = dict()
        for i in pref_as_is:
            if i in turnOffItems:
                pref_new[i] = 0
            else:
                pref_new[i] = pref_as_is[i]
        setDefault('glyphZoomViewShowItems', pref_new)
        preferencesChanged()

    def _restoreGlyphViewItems(self):
        setDefault('glyphZoomViewShowItems',
                   getExtensionDefault('restoreGlyphZoomViewShowItems'))
        preferencesChanged()
