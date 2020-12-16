# from utilities import storeConstructionsInFontLib
import imp,os
from glyphConstruction import ParseGlyphConstructionListFromString, GlyphConstructionBuilder
from vanilla import *

# import utilities

f = CurrentFont()


def constructions2columnlist(constructions):
    l = []
    for i in ParseGlyphConstructionListFromString(constructions):
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
    dict(title="", key="active", cell=CheckBoxListCell(), width=17),
    dict(title="compo", width=130, editable=True),
    dict(title="base", width=50,  editable=True),
    dict(title="construction", editable=False),
]


class GlyphConstructionEditor():
    def __init__(self):
        self.w = Window((600, 400), minSize=(400, 100),title="GlyphConstuctions Editor")
        self.w.l = List(
            (10, 10, 400, -10),

            [],
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
        self.w.dupConstruction = Button(
            (430, y+30, -10, 22), "dulpicate", callback=self.dupConstruction)
        self.w.delConstruction = Button(
            (430, y+60, -10, 22), "delete", callback=self.delConstruction)
        self.w.reloadDefaultSet = Button(
            (430, y+90, -10, 22), "reload defaults", callback=self.reloadConstruction)

        self.w.open()
        self.load()

    def load(self):
        if f:
            if 'nl.hallotype.glyphConstructions' in f.lib.keys():
                self.w.l.set(f.lib['nl.hallotype.glyphConstructions'])
            else:
                self.reloadConstruction(None)
        else:
            self.reloadConstruction(None)


    def reloadConstruction(self, sender):
        """
        throw away custom contrustions and load default
        """
        # print(os.getcwd())
        path = "/Users/thom/Library/Application Support/RoboFont/scripts/*DiacriticsWorkflow/_glyphContructions_basic+.py"
        bc = imp.load_source('txt', path)
        asList = ParseGlyphConstructionListFromString(bc.basics)
        asDict = []
        for i in asList:
            if not i: continue
            if i.find("+") != i.rfind("+"):
                continue
            compo = i.split("=")[0][:-1]
            base = i.split("=")[1][1:].split("+")[0].strip()
            accent = i.split("=")[1][1:].split("+")[1].strip().split("@")[0]
            anchor = i.split("=")[1][1:].split("+")[1].strip().split("@")[1]
            # for now only one accent@anchor pair!
            construction = i.split("+")[1].strip()
            asDict.append(dict(
                active=True,
                compo=compo,
                base=base,
                accent=accent,
                anchor=anchor,
                construction=construction,

            ))

        if f:
            f.lib['nl.hallotype.glyphConstructions'] = asDict
            self.w.l.set(f.lib['nl.hallotype.glyphConstructions'])
        else:
            self.w.l.set(asDict)
        # clear Edits
        self.w.editCompo.set("")
        self.w.editBase.set("")
        self.w.editAccent.set("")
        self.w.editAnchor.set("")


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
        n = {"active": True, "compo": 'x', 'base': 'x',
             'accent': 'x', "anchor": 'a', 'construction': 'x@a'}
        l = self.w.l
        l.insert(0, n)
        self.w.l.set(l)
        index = self.w.l.get().index(n)
        self.w.l.setSelection([index])
        self.w.l.scrollToSelection()

    def dupConstruction(self, sender):
        n = {"active": True, "compo": self.w.editCompo.get(), 'base': self.w.editBase.get(),
             'accent': self.w.editAccent.get(), "anchor": self.w.editAnchor.get(), 'construction': self.w.editAccent.get()+'@'+self.w.editAnchor.get()}
        l = self.w.l
        l.insert(0, n)
        self.w.l.set(l)
        index = self.w.l.get().index(n)
        self.w.l.setSelection([index])
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
        l[index]['accent'] = self.w.editAccent.get()
        l[index]['anchor'] = self.w.editAnchor.get()
        l[index]['construction'] = "@".join(
            [self.w.editAccent.get(), self.w.editAnchor.get()])
        self.w.l.set(l)

        self.updateFontConstruction()

    def updateFontConstruction(self):
        __doc__ = """..."""
        l = self.w.l.get()
        # s = """"""
        # # Ytilde = Y+tilde@top

        # for i in l:``
        #     c = "%s = %s+%s\n" % (i['compo'], i['base'], i['construction'])
        #     s += c

        f.lib['nl.hallotype.glyphConstructions'] = l


GlyphConstructionEditor()
