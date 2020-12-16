"""
todo:
    - interface
    - multi accents
"""


from glyphConstruction import ParseGlyphConstructionListFromString, GlyphConstructionBuilder
import imp
import os

font = f = CurrentFont()

smallcapsSuffix = ".sc" # not needed anymore 20201210
capThreshold = 600




def reloadConstruction():
    """
    throw away custom Constructions and load default
    """
    path = "/Users/thom/Library/Application Support/RoboFont/scripts/*DiacriticsWorkflow/_glyphContructionsRF3.py"
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

def doGlyph(construction):
    pass

def processGlyph(font, comp, base, accent, anchor):
    """
    This function compiles the glyph,
    if baseGlyph or accent not in the font it wont compile
    if anchors are missing it wont compile

    big chunk came from https://robofont.com/documentation/how-tos/building-accented-glyphs-with-a-script/
    """
    if base not in font.keys():
        return "Not found: " + base

    inBase, height = anchorInGlyph(anchor, font[base])
    if inBase and height > capThreshold:
        if accent+".cap" in font.keys():
            accent = accent+".cap"
    if accent not in font.keys():
        return "Not found: " + accent

    inAccent, height = anchorInGlyph(anchor, font[accent])

    if not inBase:
        return "Not found: %s in %s" % (anchor, base)
    if not inAccent:
        return "Not found: %s in %s" % (anchor, accent)

    construction = "%s = %s + %s@%s" % (comp, base, accent, anchor)

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

    


def isCap(glyphname):
    return(glyphname[0] == glyphname[0].upper())


def anchorInGlyph(anchor, glyph):
    for a in glyph.anchors:
        if a.name == anchor:
            return (True, a.y)
        if a.name == "_"+anchor:
            return (True, a.y)
    return (False, None)


log = []


# define glyph constructions
test = '''\
agrave = a + grave@top
aacute = a + acute@top
iogonek = i + ogonek@ogonek
Iacute = I+acute@top+acute@top
bdkjn = re+acute@top

'''


batchConstructions = []
# try to load font constructions
if 'nl.hallotype.glyphConstructions' in f.lib:
    batchConstructions = list(f.lib['nl.hallotype.glyphConstructions']) # copy of list otherwise the lowers get added!
# else:
#     # load extrenal contructions
#     reloadConstruction()
#     batchConstructions = f.lib['nl.hallotype.glyphConstructions']

compos = []
for i in batchConstructions:
    compos.append(i['compo'])

# add lowercase
for i in batchConstructions:
    if i['base'][0] == i['base'][0].upper():
        if i['compo'].lower() not in compos:
            j = dict(i)
            j['base'] = j['base'].lower()
            j['compo'] = j['compo'].lower()
    
            batchConstructions.append(j)

# collect all baseGlyphs
baseGlyphs = set()
for i in batchConstructions:
    baseGlyphs.add(i['base'])

# search for baseGlyphs.suffix in font
foundSuffixedGlyphNames = {}
for bgn in baseGlyphs:
    for gn in f.keys():
        if gn.startswith(bgn+"."):
            if bgn in foundSuffixedGlyphNames:
                foundSuffixedGlyphNames[bgn].append(gn)
            else:
                foundSuffixedGlyphNames[bgn] = [gn]


for construction in batchConstructions:
    if construction['active'] == True:
        bases = [construction['base']]
        if construction['base'] in foundSuffixedGlyphNames:
            bases += foundSuffixedGlyphNames[construction['base']]
        # print(bases)
        for base in bases:
            suffix = ""
            if "." in base and "." not in construction['compo']:
                suffix = "."+".".join(base.split(".")[1:])
                # print(suffix)
            r = processGlyph(font, 
                construction['compo']+suffix, 
                base, 
                construction['accent'], 
                construction['anchor']
            )
            if r and r not in log:
                log.append(r)

        # # # smallcaps
        # if isCap(construction['base']):
        #     r = processGlyph(font, 
        #         construction['compo']+smallcapsSuffix, 
        #         construction['base']+smallcapsSuffix, 
        #         construction['accent'], 
        #         construction['anchor']
        #         )
        #     if r and r not in log:
        #         log.append(r)

for i in log: print(i)



