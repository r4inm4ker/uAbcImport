# from alembic import Abc
import pymel.core as pm
import sys
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMaya as om

kPluginCmdName = "uAbcImport"

class NodeLogger(object):
    """
    log added nodes
    """
    def __init__(self):
        self._nodes = []

    def logNode(self, node, *args, **kwargs):
        self._nodes.append(pm.PyNode(node))

    @property
    def nodes(self):
        return self._nodes

# Command
class scriptedCommand(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
        self.nodes = None
        self.abcPath = None

    def doImport(self,abcPath):
        try:
            nodeLogger = NodeLogger()
            mid = om.MDGMessage.addNodeAddedCallback(nodeLogger.logNode)
            pm.AbcImport(abcPath)
        finally:
            om.MMessage.removeCallback(mid)

        self.nodes = nodeLogger.nodes
        self.abcPath = abcPath

    # Invoked when the command is run.
    def doIt(self, argList):
        abcPath = argList.asString(0)
        self.doImport(abcPath)

    def redoIt(self):
        self.doImport(self.abcPath)

    def undoIt(self, *args, **kwargs):
        try:
            pm.undoInfo(stateWithoutFlush=False)
            pm.delete(self.nodes)
        finally:
            pm.undoInfo(stateWithoutFlush=True)

    def isUndoable(self):
        return True

# Creator
def cmdCreator():
    return OpenMayaMPx.asMPxPtr(scriptedCommand())


# Initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand(kPluginCmdName, cmdCreator)
    except:
        sys.stderr.write("Failed to register command: %s\n" % kPluginCmdName)
        raise


# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(kPluginCmdName)
    except:
        sys.stderr.write("Failed to unregister command: %s\n" % kPluginCmdName)
