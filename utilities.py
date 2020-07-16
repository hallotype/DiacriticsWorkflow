from _glyphContructionsRF3 import *
from glyphConstruction import ParseGlyphConstructionListFromString, GlyphConstructionBuilder
import imp


def makeSuperDict():
    superdict = sd = {}
    cs = CurrentFont().lib['nl.hallotype.glyphConstructions']
    from glyphConstruction import ParseGlyphConstructionListFromString
    for construction in ParseGlyphConstructionListFromString(cs):
        compo = construction.split("=")[0][:-1]
        base = construction.split("=")[1][1:].split("+")[0].strip()
        accent = construction.split("=")[1][1:].split(
            "+")[1].strip().split("@")[0]
        anchor = construction.split("=")[1][1:].split(
            "+")[1].strip().split("@")[1]

        if base not in sd:
            sd[base] = {}
        if accent not in sd:
            sd[accent] = {}
        if anchor not in sd:
            sd[anchor] = {}
        if compo not in sd:
            sd[compo] = {}

        if base not in sd[accent]:
            sd[accent][base] = {}
        if base not in sd[anchor]:
            sd[anchor][base] = {}
        if base not in sd[compo]:
            sd[compo][base] = {}

        if accent not in sd[base]:
            sd[base][accent] = {}
        if accent not in sd[anchor]:
            sd[anchor][accent] = {}
        if accent not in sd[compo]:
            sd[compo][accent] = {}

        if anchor not in sd[base]:
            sd[base][anchor] = {}
        if anchor not in sd[accent]:
            sd[accent][anchor] = {}
        if anchor not in sd[compo]:
            sd[compo][anchor] = {}

        if compo not in sd[base]:
            sd[base][compo] = {}
        if compo not in sd[accent]:
            sd[accent][compo] = {}
        if compo not in sd[anchor]:
            sd[anchor][compo] = {}

        if anchor not in sd[base][accent]:
            sd[base][accent][anchor] = compo
        if accent not in sd[base][anchor]:
            sd[base][anchor][accent] = compo
    return sd


print(sd['racute'])


def makeLookupDicts(myset):
    b = {}
    a = {}
    constructions = ParseGlyphConstructionListFromString(myset)
    # print(constructions)
    for construction in constructions:
        if construction.find("+") != construction.rfind("+"):
            continue  # kill doubles for now
        compo = construction.split("=")[0][:-1]
        base = construction.split("=")[1][1:].split("+")[0].strip()
        accent = construction.split("=")[1][1:].split(
            "+")[1].strip().split("@")[0]
        anchor = construction.split("=")[1][1:].split(
            "+")[1].strip().split("@")[1]
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


def storeConstructionsInFontLib(font, set):
    font.lib['nl.hallotype.glyphConstructions'] = set
