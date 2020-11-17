from glyphConstruction import ParseGlyphConstructionListFromString, GlyphConstructionBuilder
import imp
import os

font = f = CurrentFont()

def processGlyph(font, comp, base, accent, anchor):
    if base not in font.keys():
        return
    if accent not in font.keys():
        return

    inBase, height = anchorInGlyph(anchor, font[base])
    if inBase and height > 600:
        if accent+".cap" in font.keys():
            accent = accent+".cap"
    inAccent, height = anchorInGlyph(anchor, font[accent])

    if not inBase:
        return
    if not inAccent:
        return 

    construction = "%s = %s + %s@%s" % (comp, base, accent, anchor)

    # print(construction) #line

    # build a construction glyph
    constructionGlyph = GlyphConstructionBuilder(construction, font)

    # if the construction for this glyph was preceded by `?`
    # and the glyph already exists in the font, skip it
    # if constructionGlyph.name in font and constructionGlyph.name in ignoreExisting:
    #     return

    # get the destination glyph in the font
    glyph = font.newGlyph(constructionGlyph.name, clear=True)

    # draw the construction glyph into the destination glyph
    constructionGlyph.draw(glyph.getPen())

    # copy construction glyph attributes to the destination glyph
    glyph.name = constructionGlyph.name
    glyph.unicode = constructionGlyph.unicode
    glyph.width = constructionGlyph.width
    glyph.markColor = 1, 1, 0, 0.5

    # if no unicode was given, try to set it automatically
    if glyph.unicode is None:
        glyph.autoUnicodes()


# define glyph constructions
test = '''\
agrave = a + grave@top
aacute = a + acute@top
iogonek = i + ogonek@ogonek
Iacute = I+acute@top+acute@top
bdkjn = re+acute@top

'''


def anchorInGlyph(anchor, glyph):
    for a in glyph.anchors:
        if a.name == anchor:
            return (True, a.y)
        if a.name == "_"+anchor:
            return (True, a.y)
    return (False, None)


# try to load font constructions
if 'nl.hallotype.glyphConstructions' in f.lib:
    batchConstructions = f.lib['nl.hallotype.glyphConstructions']
else:
    # load default set
    path = "_glyphContructionsRF3.py"
    bc = imp.load_source('txt', path)
    asList = ParseGlyphConstructionListFromString(bc.basics)
    asDict = []
    for i in asList:
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

    f.lib['nl.hallotype.glyphConstructions'] = asDict
    batchConstructions = f.lib['nl.hallotype.glyphConstructions']


for construction in batchConstructions:
    if construction['active'] == True:
        processGlyph(font, 
            construction['compo'], 
            construction['base'], 
            construction['accent'], 
            construction['anchor']
        )



