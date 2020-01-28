#!/usr/bin/env python2
# -*- coding: utf-8 -*-


"""
Created on Tue Jul 10 20:54:51 2018

@author: hen
"""

from __future__ import print_function

import os
import os.path
#import exifread
import shutil
import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import sys

class PictureManager:
    
    def __init__(self, source, target):
        self.sourcepath = source
        self.targetpath = target
        self.quiet = False
        self.force = False
        if not self.sourcepath.endswith('/'):
            self.sourcepath += ('/')
        if not self.targetpath.endswith('/'):
            self.targetpath += ('/')       
        
    def copyAndRename(self):
        for filename in os.listdir(self.sourcepath):
            datename = self.getDateName(self.sourcepath + filename)
            if not datename: 
                continue
            shutil.copyfile(self.sourcepath + filename, self.targetpath + datename)
            
    def moveRenamed(self):
        moveall = self.force
        noall = False
        for filename in [f for f in os.listdir(self.sourcepath) if not os.path.isdir(self.sourcepath + f)] :
            try:
                datename = self.getDateName(self.sourcepath + filename)
            except Exception as ex:
                print(str(ex))
                if noall:
                    continue
                if not moveall:
                    ans = input("move anyway? (Y/n) ")
                    if ans == "yesall":
                        moveall = True
                    elif ans == "noall":
                        noall = True
                        continue
                    elif ans != "" and ans.lower() != "y":
                        continue
                datename = filename
            if not datename:
                continue
            shutil.move(self.sourcepath + filename, self.targetpath + datename)
            
            
    def copySorted(self):
        for filename in os.listdir(self.sourcepath):
            try:
                if os.path.isdir(self.sourcepath + filename):
                    continue
                folderpath = self.targetpath + PictureManager\
                    .folderDateName(self.sourcepath + filename) + '/'
                if not folderpath:
                    continue
                if not os.path.isdir(folderpath):
                    os.mkdir(folderpath)
                if os.path.isfile(folderpath + filename):
                    if not self.quiet: 
                        print("will not copy " + filename + ": file exists in target folder")
                    continue
                shutil.copyfile(self.sourcepath + filename, folderpath + filename)
            except Exception as ex:
                print(str(ex))
                continue
            
    def moveSorted(self):
        for filename in os.listdir(self.targetpath):
            try:
                if os.path.isdir(self.sourcepath + filename):
                    continue
                if PictureManager.isResponsible(filename):
                    if not self.quiet:
                        print("processing " + filename + "... ", end='')  
                    folderpath = self.targetpath + PictureManager\
                        .folderDateName(self.sourcepath + filename) + '/'
                    if not folderpath:
                        continue
                    if not os.path.isdir(folderpath):
                        os.mkdir(folderpath)
                    if os.path.isfile(folderpath + filename):
                        if not self.quiet:
                            print("abort: " + ": file exists in target folder (" + folderpath + ")")
                        continue
                    shutil.move(self.sourcepath + filename, folderpath + filename)
                    if not self.quiet:
                        print("done.")
                else:
                    if not self.quiet:
                	    print("skipping " + filename + ".")
            except Exception as ex:
                try:
                   print("failed: " + str(ex))
                except:
                    print("this did not end well...")
                continue       
            
    @staticmethod
    def isResponsible(filename):
        return filename.lower().endswith(".jpg")  \
            or filename.lower().endswith(".jpeg") \
            or filename.lower().endswith(".mov")
                    
        
    @staticmethod
    def getDateName(path):
        dt = PictureManager.getExifDateTime(path)
        if not dt:
            return None
        return "{0:04}-{1:02}-{2:02}_{3:02}-{4:02}-{5:02}"\
            .format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)\
            + '.' + path.split('.')[-1]
        
    @staticmethod
    def getExifDateTime(path):
        if os.path.isdir(path):
            return None
        if not os.path.isfile(path):
            raise Exception("Error while processing " + path + ": file does not exist.")
        for (k, v) in Image.open(path)._getexif().items():
            tag = str(TAGS.get(k))
            if tag != None and tag.lower().startswith('datetime'):
                dt = str(v).split(' ')
                date = dt[0].split(':')
                time = dt[1].split(':')
                year, month, day = int(date[0]), int(date[1]), int(date[2])
                hour, minute, second = int(time[0]), int(time[1]), int(time[2])
                return datetime.datetime(year, month, day, hour, minute, second)
        raise Exception("Error while processing " + path 
                        + ": no DateTime information found in exif information")
    @staticmethod
    def getDateTimeLastChange(path):
        lastChange = os.stat(path).st_mtime
        return datetime.datetime.fromtimestamp(lastChange)
        
    @staticmethod
    def folderDateName(path):
        try:
            dt = PictureManager.getExifDateTime(path)
        except Exception as ex:
            if str(ex).endswith(": no DateTime information found in exif information") \
                or str(ex).endswith(": no exif information found."):
                dt = PictureManager.getDateTimeLastChange(path)
            else:
                raise ex
        if not dt:
            return None
        return "{0:04}-{1:02}".format(dt.year, dt.month)
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: " + sys.argv[0] + " SOURCEPATH [TARGETPATH]")
        exit()
    
    force = False
    quiet = False

    sourcePath = sys.argv[1]
    if len(sys.argv) < 3:
        targetPath = sourcePath
    else:
        targetPath = sys.argv[2]

    if "--force" in sys.argv:
        force = True

    if "--quiet" in sys.argv:
        quiet = True

    if not os.path.isdir(sourcePath) :
        print("error: source '" + sourcePath + "'has to be existing directories")
        exit()

    if  not os.path.isdir(targetPath):
        print("error: target has to be existing directories")
        exit()


    pm = PictureManager(sourcePath, targetPath)
    pm.force = force
    pm.quiet = quiet

    if not force:
        ans = input("rename pictures (date/time tag)? (Y/n)")
    if force or ans == "" or ans.lower() == "y":
        pm.moveRenamed()
    
    if not force:
        ans = input("sort pictures? (Y/n)")
    if force or ans == "" or ans.lower() == "y":
        pm.moveSorted()
        
        
