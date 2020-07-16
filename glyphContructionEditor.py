from utilities import storeConstructionsInFontLib
import imp
from glyphConstruction import ParseGlyphConstructionListFromString, GlyphConstructionBuilder
from vanilla import *

import utilities

f = CurrentFont()


def constructions2columnlist(constructions):
    l = []
    for i in ParseGlyphConstructionListFromString(f.lib['nl.hallotype.glyphConstructions']):
        if i.find("+") != i.rfind("+"):
            continue
        comp = i.split("=")[0][:-1]
        base = i.split("=")[1][1:].split("+")[0].strip()
        accent = i.split("=")[1][1:].split("+")[1].strip().split("@")[0]
        anchor = i.split("=")[1][1:].split("+")[1].strip().split("@")[1]
        # for now only one accent@anchor pair!
        constr = i.split("+")[1].strip()

        d = dict(
            compo=comp,
            base=base,
            construction=constr
        )
        l.append(d)
    return l


columnDescriptions = [
    dict(title="compo", width=100, editable=True),
    dict(title="base", width=50,  editable=True),
    dict(title="construction", editable=False),
]


class GlyphConstructionEditor():
    def __init__(self):
        self.w = Window((600, 400), minSize=(400, 100),)
        self.w.l = List(
            (10, 10, 400, -10),

            constructions2columnlist(f.lib['nl.hallotype.glyphConstructions']),
            columnDescriptions=columnDescriptions,
            selectionCallback=self.loadForEdit,
        )
        y = 10
        self.w.compotxt = TextBox((430, y, -10, 22), "Compo", sizeStyle='mini')
        self.w.editCompo = EditText((430, y+16, -10, 22),)
        y += 50
        self.w.basetxt = TextBox((430, y, -10, 22), "Base", sizeStyle='mini')
        self.w.editBase = EditText((430, y+16, -10, 22),)
        y += 50
        self.w.accenttxt = TextBox(
            (430, y, -10, 22), "Accent", sizeStyle='mini')
        self.w.editAccent = EditText((430, y+16, -10, 22),)
        y += 50
        self.w.anchorrtxt = TextBox(
            (430, y, -10, 22), "Anchor", sizeStyle='mini')
        self.w.editAnchor = EditText((430, y+16, -10, 22),)
        y += 55
        self.w.update = Button((430, y, -10, 22),
                               "update", callback=self.updateList)
        y += 40
        self.w.hl = HorizontalLine((430, y, -10, 1))
        y += 15
        self.w.newConstruction = Button(
            (430, y, -10, 22), "new", callback=self.newConstruction)
        self.w.delConstruction = Button(
            (430, y+30, -10, 22), "delete", callback=self.delConstruction)
        self.w.reloadDefaultSet = Button(
            (430, y+60, -10, 22), "reload defaults", callback=self.reloadConstruction)

        self.w.open()

    def reloadConstruction(self, sender):
        path = "/Users/thom/Library/Application Support/RoboFont/scripts/*accent/_glyphContructionsRF3.py"
        bc = imp.load_source('txt', path)
        f.lib['nl.hallotype.glyphConstructions'] = bc.basics
        self.w.l.set(constructions2columnlist(
            f.lib['nl.hallotype.glyphConstructions']),)

    def delConstruction(self, sender):
        sel = self.w.l.getSelection()
        l = self.w.l.get()
        items = []
        for i in sel:
            items.append(l[i])
        # print(items)
        for i in items:
            l.remove(i)
        self.w.l.set(l)
        self.updateFontConstruction()

    def newConstruction(self, sender):
        n = {"compo": 'x', 'base': 'x', 'construction': 'x@x'}
        l = self.w.l.get()
        l.insert(0, n)
        self.w.l.set(l)
        self.w.l.setSelection([0])
        self.w.l.scrollToSelection()

    def loadForEdit(self, sender):
        if not sender.getSelection():
            return
        item = sender.get()[sender.getSelection()[0]]
        accent, anchor = item['construction'].split("@")
        # print(accent, anchor)
        self.w.editCompo.set(item['compo'])
        self.w.editBase.set(item['base'])
        self.w.editAccent.set(accent)
        self.w.editAnchor.set(anchor)
        self.edit = item

    def updateList(self, sender):
        __doc__ = """when click update button the list gets rebuild
        and _f.lib['nl.hallotype.glyphConstructions']_ gets updated"""

        l = self.w.l.get()
        e = self.edit
        index = l.index(e)
        l[index]['compo'] = self.w.editCompo.get()
        l[index]['base'] = self.w.editBase.get()
        l[index]['construction'] = "@".join(
            [self.w.editAccent.get(), self.w.editAnchor.get()])
        self.w.l.set(l)

        self.updateFontConstruction()

    def updateFontConstruction(self):
        __doc__ = """take the list and turn it into string and store"""
        l = self.w.l.get()
        s = """"""
        # Ytilde = Y+tilde@top

        for i in l:
            c = "%s = %s+%s\n" % (i['compo'], i['base'], i['construction'])
            s += c

        f.lib['nl.hallotype.glyphConstructions'] = s


GlyphConstructionEditor()
