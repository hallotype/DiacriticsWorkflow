# Diacritics Workflow
A toolkit for working on diacritics/accents in RoboFont

Thom Janssen 072020


### GlyphConstructions
`GlyphConstructions` are the basis for these tools. There is only one source so is no double data and/or out of sync things. Only the capital Constructions are in the this list. The workflow translate it to lowercase as well as all suffixes. Except when the Construction is different than the capital Construction it is added to the Constructions.

```
Agrave = A+grave@top
Aacute = A+acute@top
Acircumflex = A+circumflex@top
Atilde = A+tilde@top
Adieresis = A+dieresis@top
Aring = A+ring@ring
Ccedilla = C+cedilla@bottom
Egrave = E+grave@top
…
Dcaron = D+caron@top
dcaron = d+caronslovak@right   # <- construction is different for lowercase
…
```

The GlyphConstruction are stored in the font.lib. The font is in charge of what diacritics are important for the project.

### Editor

![screenshot](images/screenGlyphConstrEditor.png)

Edit the database.

---

### positioning observer

![screenshot](images/screen_Aring.png)
In a dialog all the accent-anchor combinations are visible for this base glyph. Positioning the anchors should be easier this way. Double click on the accent-name in the list loads that accent glyph in the current glyph window. This tools works in both ways: baseGlyph>accents and accents>baseGlyphs:
![screenshot](images/screenAccent2baseGlyph.png)
If an anchor is missing, there is a warning:
![screenshot](images/screen_missingAnchor.png)
Also if an anchor is missing there will be a button in the Window 'add missing anchors'. This will place the anchors roughly in the right spot. 

---

###  batch generate

A script reads the glyphConstructions and generates all the glyphs.

---

### helpers

#### FontBoundingBox

![screenshot](images/screen_fbb.png)

The FontBoundingBox is an other observer that keeps track of the -yes- font bounding box. A little dialog tells you which glyphs are (among others) responsable for these extremes. And it draws the box itself.
