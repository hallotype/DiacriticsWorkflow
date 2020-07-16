"""
todo:
    - interface
    - cap
"""


from glyphConstruction import ParseGlyphConstructionListFromString, GlyphConstructionBuilder
import imp
import os
f = CurrentFont()

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
    # load extrenal contructions
    path = "/Users/thom/Library/Application Support/RoboFont/scripts/*accent/_glyphContructionsRF3.py"
    bc = imp.load_source('txt', path)
    batchConstructions = bc.basics

#batchConstructions = test


# get the actual glyph constructions from text
constructions = ParseGlyphConstructionListFromString(batchConstructions)

# get the current font
font = CurrentFont()

# collect glyphs to ignore if they already exist in the font
ignoreExisting = [L.split('=')[0].strip()[1:]
                  for L in batchConstructions.split('\n') if L.startswith('?')]

# iterate over all glyph constructions
for construction in constructions:
    if construction.find("+") != construction.rfind("+"):
        continue
    comp = construction.split("=")[0][:-1]
    base = construction.split("=")[1][1:].split("+")[0].strip()
    accent = construction.split("=")[1][1:].split("+")[1].strip().split("@")[0]
    anchor = construction.split("=")[1][1:].split("+")[1].strip().split("@")[1]

    if base not in font.keys():
        continue
    if accent not in font.keys():
        continue

    inBase, height = anchorInGlyph(anchor, font[base])
    if inBase and height > 600:
        if accent+".cap" in font.keys():
            accent = accent+".cap"
    inAccent, height = anchorInGlyph(anchor, font[accent])

    if not inBase:
        continue
    if not inAccent:
        continue

    construction = "%s = %s + %s@%s" % (comp, base, accent, anchor)

    # print(construction) #line

    # build a construction glyph
    constructionGlyph = GlyphConstructionBuilder(construction, font)

    # if the construction for this glyph was preceded by `?`
    # and the glyph already exists in the font, skip it
    if constructionGlyph.name in font and constructionGlyph.name in ignoreExisting:
        continue

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
