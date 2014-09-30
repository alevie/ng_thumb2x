#!/usr/bin/env python
# Filename: ng_thumb2x.py
# Author: levies@gmail.com
# Date: 2013-10-13
# Purpose: Generate retina thumbnails for the Wordpress Nextgen Gallery Plugin

import os
import sys
import Image
import Queue
import threading
from PIL import ImageOps

class Threads(threading.Thread):
  
  def __init__(self, queue, thumbsize):
    threading.Thread.__init__(self)
    self.queue = queue
    self.h = thumbsize['height']
    self.w = thumbsize['width']
    self.h_r = self.h*2
    self.w_r = self.w*2

  def run(self):
    global tcount, keepalive
    while keepalive == True:
      try:
        directory, filename = self.queue.get(False)
      except:
        tcount = tcount - 1
        print 'tcount:', tcount
        break
      else:
        self.make_thumb(directory,filename)

  def make_thumb(self,directory,filename):
      fullpath = os.path.join(directory,filename)
      newpath = os.path.join(directory,'thumbs','thumbs_'+filename[0:-4]+'.jpg')
      newpath_r = os.path.join(directory,'thumbs','thumbs_'+filename[0:-4]+'@2x.jpg')

      # create normal thumbnail
      image = Image.open(fullpath)
      image = ImageOps.fit(image, (self.w, self.h), method=Image.ANTIALIAS)
      image.save(newpath,"JPEG",quality=90)
      
      # create retina thumbnail
      image_r = Image.open(fullpath)
      image_r = ImageOps.fit(image_r, (self.w_r, self.h_r), method=Image.ANTIALIAS)
      image_r.save(newpath_r,"JPEG",quality=50)

      print newpath, newpath_r

def main():
  #### INPUTS #############################################################################
  startdir = '/var/www/html/example.com/wp-content/gallery'
  thumbsize = {'width':175,'height':116}
  #### END INPUTS #########################################################################

  global tcount, keepalive
  tcount = 10
  keepalive=True # parameter to break execution
  queue = Queue.Queue(0)
  for directory, dirs, files in os.walk(startdir):
    print directory
    for filename in files:
      if (filename[-4:] in ['.jpg','.JPG']) and ('thumbs' not in directory):
        queue.put([directory, filename])
  # shrink the worker pool to number in queue if necessary
  if queue.qsize() < tcount:
    tcount = queue.qsize()
  # start the threads
  for x in range(tcount):
    Threads(queue,thumbsize).start()

  raw_input()
  keepalive = False


if __name__ == "__main__":
  main()
  