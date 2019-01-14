#May have to run this as Administrator if Python is installed where
#Admin privledges are required to write into the Python install sub/folder

path_to_monitor = r'C:\geoevent_input\locateXT_in'
path_to_output = r'\\wdcsol0000046\locatext_in'

find_dates = True #use True or False to search for dates

find_polar_UTM_MGRS = False #use True or False to search for polar coordinates

#gaz_file_path = r''
gaz_file_path = r''
fuzzy_percent_error_level = 0 #0 - 30

#ca_file_path = r''
ca_file_path = r''



###################################################

#portions based on http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html
import os
import sys
import win32file
import win32event
import win32con
import win32api
import time
import queue
import threading
import tempfile
import datetime


q = queue.Queue()

#--this is what is running on a worker thread
#  it processes each file in the queue
def worker():
  #print("worker\n")
  import re
  import comtypes.client as cc
  import comtypes
  tlb_id = comtypes.GUID("{310BB2DC-AB12-4DE3-839C-1E7CDEAD68A3}")
  cc.GetModule((tlb_id, 1, 3))
  import comtypes.gen.ct_LocateXT_API as LXT_API

  ICoordSearch = cc.CreateObject(LXT_API.CoordinateSearching,None,None,LXT_API.ICoordinateSearching2)
  ICoordSearch.UTM_NorthPolar = find_polar_UTM_MGRS
  ICoordSearch.UTM_SouthPolar = find_polar_UTM_MGRS
  ICoordSearch.MGRS_NorthPolar = find_polar_UTM_MGRS
  ICoordSearch.MGRS_SouthPolar = find_polar_UTM_MGRS
  
  ILxtMgr = cc.CreateObject(LXT_API.LocateXT_Manager2, None, None, LXT_API.ILocateXT_Manager3)
  ILxtMgr.SetSearcher(ICoordSearch)
  

  if find_dates:
    IDateSearch = cc.CreateObject(LXT_API.DateSearching,None,None,LXT_API.IDateSearching)
    ILxtMgr.SetSearcher(IDateSearch)

  if gaz_file_path:
    #print("gaz: ",gaz_file_path," err: ",fuzzy_percent_error_level)
    IGazSearch = cc.CreateObject(LXT_API.GazetteerSearching,None,None,LXT_API.IGazetteerSearching)
    IGazSearch.GazetteerFile = os.path.abspath(gaz_file_path)
    IGazSearch.FuzzyErrorLevelPercent= fuzzy_percent_error_level
    ILxtMgr.SetSearcher(IGazSearch)

  if ca_file_path:
    #print("ca: ",ca_file_path)
    ICASearch = cc.CreateObject(LXT_API.CustomAttributeSearching,None,None,LXT_API.ICustomAttributeSearching)
    ICASearch.CustomAttributesFile = os.path.abspath(ca_file_path)
    ILxtMgr.SetSearcher(ICASearch)

  out_path = os.path.abspath (path_to_output)
  
  while True:
    file = q.get()#blocks until something in q
    if file is None:
      break

    #loop until the file can be opened exclusively
    #this ensures the file is done being written/copied
    #and can be processed further
    success = False
    count = 0
    while not success and count < 20:
      try:
        hFile = win32file.CreateFile (
                  full_filename,
                  win32con.GENERIC_READ | win32con.GENERIC_WRITE,
                  0,#exclusive access
                  None,
                  win32con.OPEN_EXISTING,
                  win32con.FILE_ATTRIBUTE_NORMAL,
                  None
                )

      except:
        #print("Unexpected error:", sys.exc_info()[1])
        #raise
        pass
      else:
        #print("handle = ", hFile)
        win32api.CloseHandle(hFile)
        success = True

      count += 1
      time.sleep(0.5)

    if success:
      #file can be processed
      print("Processing: ",file)
      csvOut = ILxtMgr.Scan(LXT_API.lxtInputTypeFilename, file, LXT_API.lxtOutputTypeCSV)
      csvOutAscii = re.sub(r'[^\x00-\x7f]',r' ',csvOut)#replace every character NOT in 0x00 - 0x7f with space
      #print(csvOutAscii)
      #eliminate embedded carriage returns
      csvByteArray = bytearray(csvOutAscii,'ascii','replace')#also replaces every char NOT ASCII, but with '?'
      insideQuotes = False
      i = 0
      while i < (len(csvByteArray) - 1):
        #if i < 100:
        #  print("processing i = ",i,"  : ",csvByteArray[i],"\n")
        if insideQuotes:
          #print("insideQuotes\n")
          if 34 == csvByteArray[i]:
            if 34 != csvByteArray[i+1]:
              insideQuotes = False
            else:
              i += 1
          elif (13 == csvByteArray[i]) or (10 == csvByteArray[i]):
            csvByteArray[i] = 32
        elif 34 == csvByteArray[i]:
          insideQuotes = True
        #while loop last
        i += 1
      
      #write file
      #print(csvByteArray)      
      fd, tmpName = tempfile.mkstemp(".csv",re.sub(r'[\/:*?"<>|]',r'_',str(datetime.datetime.now())),out_path,True)
      os.write(fd,csvByteArray)
      os.close(fd)
      print("Output: ",tmpName)
             
    q.task_done()
    
  print("exiting thread")

#######################################################################

#start worker thread
t = threading.Thread(target=worker)
t.start()



#folder to monitor for dropped files
path_to_watch = os.path.abspath (path_to_monitor)

#
# FindFirstChangeNotification sets up a handle for watching
#  file changes. The first parameter is the path to be
#  watched; the second is a boolean indicating whether the
#  directories underneath the one specified are to be watched;
#  the third is a list of flags as to what kind of changes to
#  watch for. We're just looking at file additions / deletions.
#
change_handle = win32file.FindFirstChangeNotification (
  path_to_watch,
  0,
  win32con.FILE_NOTIFY_CHANGE_FILE_NAME
)

#
# Loop forever, listing any file changes. The WaitFor... will
#  time out every half a second allowing for keyboard interrupts
#  to terminate the loop.
#
try:
  print("Monitoring: ",path_to_watch)

  old_path_contents = dict ([(f, None) for f in os.listdir (path_to_watch)])
  while 1:
    result = win32event.WaitForSingleObject (change_handle, 500)

    #
    # If the WaitFor... returned because of a notification (as
    #  opposed to timing out or some error) then look for the
    #  changes in the directory contents.
    #
    if result == win32con.WAIT_OBJECT_0:
      new_path_contents = dict ([(f, None) for f in os.listdir (path_to_watch)])
      added = [f for f in new_path_contents if not f in old_path_contents]

      for f in added:
        full_filename = os.path.join(path_to_watch, f)
        print ("Detected: ", full_filename)
        q.put(full_filename)

      old_path_contents = new_path_contents
      win32file.FindNextChangeNotification (change_handle)

finally:
  #print("finally\n")
  win32file.FindCloseChangeNotification (change_handle)
  #tear down and exit
  q.put(None)
  t.join()

