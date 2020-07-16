import os
import getpass

from mojo.UI import *
from vanilla import *
from vanilla.dialogs import getFile, getFolder
from mojo.events import addObserver, removeObserver
from mojo.extensions import getExtensionDefault, setExtensionDefault
from AppKit import *

from lib.UI.toggleImageButton import ToggleImageButton
import glob
import imp
import random
import string
from operator import itemgetter


defaultKeyObservatory = "nl.thomjanssen.observatory"
_pathObsFolder = "%s.pathObsFolder" % defaultKeyObservatory
_openSettings = "%s.openSettings" % defaultKeyObservatory

# OutputWindow().clear()

user = getpass.getuser()
p = "/Users/%s/Library/Application Support/RoboFont/scripts/*observers/observatory/obs/" % user
pathObsFolder = p
# getExtensionDefault(_pathObsFolder, p)
# print(pathObsFolder+"_resources/allOffIcon.pdf")
# collect obs
# os.chdir(pathObsFolder)
# print os.getcwd()
# print p
# obsdir = os.listdir(pathObsFolder)
# print obsdir


vink = u' %s' % chr(10003)
gear = u' %s' % chr(9881)

# template for ob
listDiscription = dict(title="", checkBox=False)


class Observertory(object):
    def __init__(self):
        windowWidth = 450
        windowHeight = 500

        self.o = Window((windowWidth, windowHeight), "Observertory")

        toolbarItems = [
            dict(itemIdentifier="off",
                 label="All Off",
                 imagePath=pathObsFolder+"_resources/allOffIcon.pdf",
                 callback=self._allOff,
                 ),
            #
            dict(itemIdentifier=NSToolbarFlexibleSpaceItemIdentifier),
            #
            dict(itemIdentifier="settings",
                 label="Settings",
                 imageNamed="prefToolbarMisc",
                 callback=self.settings,
                 ),
            # dict(itemIdentifier="inspector",
            # 	label="Inspector",
            # 	imageNamed="toolbarScriptOpen",
            # 	callback=self.dummy,
            # 	),
            # dict(itemIdentifier=NSToolbarFlexibleSpaceItemIdentifier),
            # dict(itemIdentifier="remove",
            # 	label="Remove",
            # 	imageNamed="toolbarScriptOpen",
            # 	callback=self.dummy,
            # 	),
            # dict(itemIdentifier="removeEmpty",
            # 	label="Remove empty",
            # 	imageNamed="toolbarScriptOpen",
            # 	callback=self.dummy,
            # 	),
            # dict(itemIdentifier=NSToolbarFlexibleSpaceItemIdentifier),
            # dict(itemIdentifier="clipboard",
            # 	label="Clipboard",
            # 	imagePath="toolbarScriptOpen",
            # 	callback=self.dummy,
            # 	),
            # dict(itemIdentifier=NSToolbarFlexibleSpaceItemIdentifier),
        ]
        toolbar = self.o.addToolbar(
            toolbarIdentifier="name", toolbarItems=toolbarItems, addStandardItems=False)

        columnDescriptions = [
            dict(title=vink, key="checkBox", cell=CheckBoxListCell(), width=15),
            # dict(title=gear, key="settings", cell=CheckBoxListCell(), width=15),
            dict(title="observer", key="title", width=385),
            dict(title="?", key="help", cell=CheckBoxListCell(),)
        ]
        self.o.observerList = List((0, 0, -0, -30),
                                   items=[],
                                   columnDescriptions=columnDescriptions,
                                   editCallback=None,
                                   doubleClickCallback=self.doubleClickListCallback,
                                   )

        self.o.observerList.set(self.makeObserverList())

        ##

        self.o.bind("close", self._close)
        self.o.bind("resigned key", self._resigned)

        screenWidth = NSScreen.mainScreen().frame().size.width
        screenHeight = NSScreen.mainScreen().frame().size.height

        # self.o.setPosSize((screenWidth/2-windowWidth/2,
        #    windowHeight/3, windowWidth, windowHeight))
        self.o.open()
        self.o.move(0, 20)

    def settings(self, sender):
        setExtensionDefault(_openSettings, True)
        self.s = Sheet((400, 140), self.o)

        self.s.closeButton = ToggleImageButton(
            (-40, 0, 40, 40), '', bordered=0, imageNamed=NSImageNameStopProgressTemplate, callback=self._settingsClose)

        self.s.putPath = SquareButton(
            (10, 20, -50, 30), "Put a new folder with observers", callback=self._settingsPutPath)
        # self.s.currentPath = PathControl((10,60,-50,22), getExtensionDefault(_pathObsFolder), sizeStyle="small")
        self.s.currentPath = EditText(
            (10, 65, -50, 50), getExtensionDefault(_pathObsFolder), sizeStyle="small", readOnly=True)

        self.s.open()

    def _settingsPutPath(self, sender):
        path = getFolder('Where do you store your observers?')[0]
        setExtensionDefault(_pathObsFolder, path)
        self.s.currentPath.set(path)

    def _settingsClose(self, sender):
        self.s.close()
        setExtensionDefault(_openSettings, False)
        self.makeObserverList()

    def doubleClickListCallback(self, sender):
        index = sender.getSelection()[0]
        self.o.observerList.get()[index]['checkBox'] = not self.o.observerList.get()[
            index]['checkBox']

    def dummy(self, sender):
        pass

    def makeObserverList(self):
        myList = []
        self.obsFileNames = {}
        self.obsClass = {}
        for filePath in glob.glob(p+"*.py"):
            fileName = filePath.split("/")[-1]

            # no "_"
            if fileName.startswith("_"):
                continue

            uniqueObsCODE = ""
            for i in range(5):
                uniqueObsCODE += random.choice(list(string.ascii_uppercase))
            # print(uniqueObsCODE)

            ob = imp.load_source(
                str(uniqueObsCODE),
                filePath
            )
            # print(ob)

            # reload(ob)
            listDiscriptionCopy = listDiscription.copy()
            listDiscriptionCopy['title'] = ob.title
            selfKey = "%sKey" % ob.title
            if getExtensionDefault(selfKey):
                listDiscriptionCopy['checkBox'] = True
                # myList.append(listDiscptionCopy)
            self.obsFileNames[ob.title] = fileName
            self.obsClass[ob.title] = ob
            myList.append(listDiscriptionCopy)
        newlist = sorted(myList, key=itemgetter('title'))

        return newlist

    def _close(self, sender):
        # print obsFileNames
        # print (self.obsClass)
        whatToDO = self.o.observerList.get()
        # print (whatToDO)

        for ob in whatToDO:
            if ob['checkBox']:
                # print ob['title']
                self.obsClass[ob['title']].ThisObserver(active=True)
            else:
                # print "not selected: %s" % ob['title']
                self.obsClass[ob['title']].ThisObserver(active=False)

        # removeObserver(self, event)
        self.o.hide()

    def _resigned(self, sender):
        if getExtensionDefault(_openSettings) is not True:
            self._close(None)

# TOOLBAR

    def _allOff(self, sender):
        for i in self.o.observerList.get():
            i['checkBox'] = False


Observertory()
