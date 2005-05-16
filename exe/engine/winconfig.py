# ===========================================================================
# eXe config
# Copyright 2004, University of Auckland
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
The WinConfig overrides the Config class with Windows specific
configuration
"""

import logging
import sys
import os
import os.path
from exe.engine.config import Config
from exe.engine.path import path

# Constants for directory name codes
APPDATA = 0x001a
COMMON_APPDATA = 0x0023
MYDOCUMENTS = 0x000c # Code for c:\documents and settings\myuser\My Documents

# ===========================================================================
class WinConfig(Config):
    """
    The WinConfig overrides the Config class with Windows specific
    configuration
    """

    def _overrideDefaultVals(self):
        """Sets the default values
        for windows"""
        exeDir = self.exePath.dirname()
        if ("Mozilla Firefox" in os.listdir(exeDir) and 
            "firefox.exe" in os.listdir(exeDir + "\\Mozilla Firefox")):
            self.browserPath = exeDir + "\\Mozilla Firefox\\firefox"
        self.dataDir = self.__getWinFolder(MYDOCUMENTS)
        self.appDataDir = self.dataDir

    def _getConfigPathOptions(self):
        """
        Returns the best options for the
        location of the config file under windows
        """
        # Find out where our nice config file is
        folders = map(self.__getWinFolder, [APPDATA, COMMON_APPDATA])
        # Add unique dir names
        folders = [folder/'exe' for folder in folders] 
        folders.append(self.__getInstallDir())
        folders.append('.')
        # Filter out non existant folders
        from pprint import pprint
        options = [folder/'exe.conf' for folder in map(path, folders)]
        pprint(options)
        return options

    def __getWinFolder(self, code):
        """
        Gets one of the windows famous directorys
        depending on 'code'
        Possible values can be found at:
        http://msdn.microsoft.com/library/default.asp?url=/library/en-us/shellcc/platform/shell/reference/enums/csidl.asp#CSIDL_WINDOWS
        """
        from ctypes import WinDLL, create_string_buffer
        dll = WinDLL('shell32')
        # The '5' and the '0' from the below call come from
        # google: "ShellSpecialConstants site:msdn.microsoft.com"
        result = create_string_buffer(260)
        resource = dll.SHGetFolderPathA(None, code, None, 0, result)
        if resource != 0: 
            return path('')
        else: 
            return path(result.value)
                
    def __getInstallDir(self):
        """
        Returns the path to where we were installed
        """
        from _winreg import OpenKey, QueryValue, HKEY_LOCAL_MACHINE
        try:
            try:
                softwareKey = OpenKey(HKEY_LOCAL_MACHINE, 'SOFTWARE')
                exeKey = OpenKey(softwareKey, 'exe')
                return path(QueryValue(exeKey, ''))
            finally:
                exeKey.Close()
                softwareKey.Close()
        except WindowsError:
            return path('')


# ===========================================================================
