# ===========================================================================
# eXe 
# Copyright 2004-2005, University of Auckland
# Copyright 2004-2009 eXe Project, http://eXeLearning.org/
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# ===========================================================================

"""
Java Applet Idevice. Enables you to embed java applet in the browser
"""

import Image, ImageDraw
from twisted.persisted.styles import requireUpgrade
import logging

from exe.engine.idevice   import Idevice
from exe.engine.path      import Path, toUnicode
from exe.engine.persist   import Persistable
from exe.engine.resource  import Resource
from exe.engine.translate import lateTranslate

log = logging.getLogger(__name__)

# Constants
GEOGEBRA_FILE_NAMES = set(["geogebra.jar", "geogebra_algos.jar", "geogebra_cas.jar", "geogebra_export.jar", "geogebra_gui.jar", "geogebra_javascript.jar", "geogebra_main.jar", "geogebra_properties.jar", "jlatexmath.jar", "jlm_cyrillic.jar", "jlm_greek.jar"])
JCLIC_FILE_NAMES = set(["jclic.jar"])
SCRATCH_FILE_NAMES = set(["ScratchApplet.jar", "soundbank.gm"])
DESCARTES_FILE_NAMES = set(["Descartes.jar", "Descartes3.jar", "Descartes4.jar", "Descartes4Runtime.jar", "DescartesA.jar", "Descartes_A.jar", "DescartesCalc.jar", "Descartes_R.jar", "Descartes_S.jar", "descinst.jar"])

# Descartes requires scene_num 
SCENE_NUM = 1
# and could use an installed plugin
DESC_PLUGIN = 0
# ===========================================================================

class AppletIdevice(Idevice):
    """
    Java Applet Idevice. Enables you to embed java applet in the browser
    """
    persistenceVersion = 1

    def __init__(self, parentNode=None):
        """
        Sets up the idevice title and instructions etc
        """
        Idevice.__init__(self, 
                         x_(u"Java Applet"), 
                         x_(u"University of Auckland"), 
                         u"",
                         u"",
                         u"",
                             parentNode)
        self.emphasis          = Idevice.NoEmphasis
        self.appletCode        = u""
        self.type              = u"other"
        self._fileInstruc      = x_(u"""Add all the files provided for the applet
except the .txt file one at a time using the add files and upload buttons. The 
files, once loaded will be displayed beneath the Applet code field.""")
        self._codeInstruc      = x_(u""""Find the .txt file (in the applet file) 
and open it. Copy the contents of this file <ctrl A, ctrl C> into the applet 
code field.""")
        self._typeInstruc     = x_(u""" <p>If the applet you're adding was generated 
by one of the programs in this drop down, please select it, 
then add the data/applet file generated by your program. </p>
<p>eg. For Geogebra applets, select geogebra, then add the .ggb file that 
you created in Geogebra.</p>""")
        self.message          = ""
        
    # Properties    
    fileInstruc = lateTranslate('fileInstruc')
    codeInstruc = lateTranslate('codeInstruc')
    typeInstruc = lateTranslate('typeInstruc')

    global DESC_PLUGIN
    DESC_PLUGIN = 0

    def getResourcesField(self, this_resource):
        """
        implement the specific resource finding mechanism for this iDevice:
        """
        # if this_resource is listed within the iDevice's userResources, 
        # then we can assume that this_resource is indeed a valid resource, 
        # even though that has no direct field.
        # As such, merely return the resource itself, to indicate that
        # it DOES belong to this iDevice, but is not a FieldWithResources:
        if this_resource in self.userResources:
            return this_resource

        return None
       
    def getRichTextFields(self):
        """
        Like getResourcesField(), a general helper to allow nodes to search 
        through all of their fields without having to know the specifics of each
        iDevice type.  
        """
        # Applet iDevice has no rich-text fields:
        return []
        
    def burstHTML(self, i):
        """
        takes a BeautifulSoup fragment (i) and bursts its contents to 
        import this idevice from a CommonCartridge export
        """
        # Java Applet Idevice:
        #title = i.find(name='span', attrs={'class' : 'iDeviceTitle' })
        #idevice.title = title.renderContents().decode('utf-8')
        # no title for this idevice.
        # =====> WARNING: not yet loading any of the files!
        # BEWARE also of the appletCode line breaks loading as <br/>,
        # may want change this back to \n or \r\n?
        # AND: also need to load the applet type: Geogebra or Other.
        inner = i.find(name='div', attrs={'class' : 'iDevice emphasis0' })
        self.appletCode= inner.renderContents().decode('utf-8')

    def uploadFile(self, filePath):
        """
        Store the upload files in the package
        Needs to be in a package to work.
        """ 
        if self.type == "descartes" and not filePath.endswith(".jar"):
            if filePath.find(",") == -1:
                global SCENE_NUM
                SCENE_NUM = 1
            else:
                SCENE_NUM = int(filePath[:filePath.find(",")])
        if (filePath.endswith(".htm") or filePath.endswith(".html")):
            self.appletCode = self.getAppletcodeDescartes(filePath)
        else:
            log.debug(u"uploadFile "+unicode(filePath))
            resourceFile = Path(filePath)
            assert self.parentNode, _('file %s has no parentNode') % self.id
            assert self.parentNode.package, \
                    _('iDevice %s has no package') % self.parentNode.id
            if resourceFile.isfile():
                self.message = ""
                Resource(self, resourceFile)
                if self.type == "geogebra":
                    self.appletCode = self.getAppletcodeGeogebra(resourceFile.basename())
                if self.type == "jclic":
                    self.appletCode = self.getAppletcodeJClic(resourceFile.basename())
                if self.type == "scratch":
                    self.appletCode = self.getAppletcodeScratch(resourceFile.basename())
                if self.type == "descartes":
                    self.appletCode = self.getAppletcodeDescartes(resourceFile.basename())
            else:
                log.error('File %s is not a file' % resourceFile)
    
    def deleteFile(self, fileName):
        """
        Delete a selected file
        """
        for resource in self.userResources:
            if resource.storageName == fileName:
                resource.delete()
                break
            
    def getAppletcodeGeogebra(self, filename):
        """
        xhtml string for GeoGebraApplet
        """
        
        html = """
        <applet code="geogebra.GeoGebraApplet.class" archive="geogebra.jar" width="750" height="450">
            <param name="filename" value="%s">
            <param name="framePossible" value="false">
            Please <a href="http://java.sun.com/getjava"> install Java 1.4</a> (or later) to use this page.
        </applet> """ % filename
        
        return html

    def getAppletcodeJClic(self, filename):
        """
        xhtml string for JClicApplet
        """  
        html = """
        <object classid="java:JClicApplet" type="application/x-java-applet" height="600" width="800"> 
            <param name="archive" value="jclic.jar"/> 
            <param name="activitypack" value="%s"/> 
        </object> """ % filename
        
        return html

    def getAppletcodeScratch(self, project):
        """
        xhtml string for ScratchApplet
        """
        html = """
            <applet id="ProjectApplet" style="display:block" code="ScratchApplet" archive="ScratchApplet.jar" width="482" height="387">
            <param name="project" value="%s">
            Please <a href="http://java.sun.com/getjava"> install Java 1.4</a> (or later) to use this page.
        </applet> """ % project
        
        return html

    def getAppletcodeDescartes(self, filename):
        """
        xhtml string for DescartesApplet
        """
        global SCENE_NUM
        html = ""
        if not filename.endswith(".jar"):
            if filename.endswith(".html") or filename.endswith(".htm"):
                from exe.engine.beautifulsoup import BeautifulSoup, BeautifulStoneSoup   
                import urllib2
                if filename.find(",") == -1:    
                    htmlbytes = urllib2.urlopen(filename)
                else:
                    htmlbytes = urllib2.urlopen(filename[2:])
                content = htmlbytes.read()
                content = content.replace('&#130;','&#130')
                # encoding = htmlbytes.headers['content-type'].split('charset=')[-1]
                soup = BeautifulSoup(content)
                i = 0
                appletslist = []
                for ap_old in soup.findAll("applet",{"code":"Descartes.class"}):
                    for resource in reversed(self.userResources):
                        if resource._storageName != ap_old["archive"]:
                            resource.delete()
                    global DESC_PLUGIN
                    DESC_PLUGIN = 0
                    ap_old["codebase"] = "./"
                    appletslist.append(ap_old)   
                for ap_new in soup.findAll("applet",{"code":"descinst.Descartes.class"}):
                    DESC_PLUGIN = 1
                    for resource in reversed(self.userResources):
                        if resource._storageName != 'descinst.jar':
                            resource.delete()
                    ap_new["codebase"] = "./"
                    appletslist.append(ap_new)
                for x in appletslist:
                    u = ''
                    if i == SCENE_NUM -1:
                        u = unicode(x)
                        break
                    i = i+1
                html = u
        return html
          
    def copyFiles(self):
        """
        if descartes, geogebra, jclic or scratch then copy all jar files, otherwise delete all jar files.
        """
        
        for resource in reversed(self.userResources):
            resource.delete()
            
        self.appletCode = ""
        self.message = ""
        if self.type == "geogebra":
            #from exe.application import application
            from exe import globals
            ideviceDir = globals.application.config.webDir/'templates'            
            for file in GEOGEBRA_FILE_NAMES:
                filename = ideviceDir/file
                self.uploadFile(filename)
            self.appletCode = self.getAppletcodeGeogebra("")
            self.message       = ""
            self._typeInstruc  = x_(u"""Clic on AddFiles button for select the .ggb file and clic on Upload button after.""")
        if self.type == "jclic":
            #from exe.application import application
            from exe import globals
            ideviceDir = globals.application.config.webDir/'templates'            
            for file in JCLIC_FILE_NAMES:
                filename = ideviceDir/file
                self.uploadFile(filename)
            self.appletCode = self.getAppletcodeJClic("")
            self.message       = ""
            self._typeInstruc  = x_(u"""Clic on AddFiles button for select the .jclic.zip file and clic on Upload button after.<p>The activity will be visible when the HTML file will be generated from eXe.""")
        if self.type == "scratch":
            #from exe.application import application
            from exe import globals
            ideviceDir = globals.application.config.webDir/'templates'            
            for file in SCRATCH_FILE_NAMES:
                filename = ideviceDir/file
                self.uploadFile(filename)
            self.appletCode = self.getAppletcodeScratch("")
            self.message       = ""
            self._typeInstruc  = x_(u"""Clic on AddFiles button for select the .sb or .scratch file and clic on Upload button after.""")
        if self.type == "descartes":
            #from exe.application import application
            from exe import globals
            ideviceDir = globals.application.config.webDir/'templates'            
            global DESC_PLUGIN
            for file in DESCARTES_FILE_NAMES:
                filename = ideviceDir/file
                self.uploadFile(filename)
            self.appletCode = self.getAppletcodeDescartes("")
            self.message       = ""
            self._typeInstruc  = x_(u"""Please write: scene number,URL (no spaces) that include it, eg: 3,http://example.com; clic on Upload button after.""")

    def upgradeToVersion1(self):
        """
        Called to upgrade to 0.23 release
        """
        self.message       = ""
        self.type == u"other"
        self._typeInstruc  = x_(u""" <p>If the applet you're adding was generated 
by one of the programs in this drop down, please select it, 
then add the data/applet file generated by your program.""")
          
# ===========================================================================
#def register(ideviceStore):
    #"""Register with the ideviceStore"""
    #ideviceStore.extended.append(AppletIdevice())    
