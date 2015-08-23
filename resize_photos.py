#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# resize_photos.py
# Resize .jpg images within given directory reqursively and keep exiv metadata!
#
#

import os, stat, re, sys
import pyexiv2
from PIL import Image

walk_dir = sys.argv[1]

def resize_image(source_path, dest_path, size):
    # resize image
    image = Image.open(source_path)
    image.thumbnail(size, Image.ANTIALIAS)
    image.save(dest_path, "JPEG")

    # copy EXIF data
    source_image = pyexiv2.metadata.ImageMetadata(source_path)
    source_image.read()
    dest_image = pyexiv2.metadata.ImageMetadata(dest_path)
    dest_image.read()
    source_image.copy(dest_image)
     
    # set EXIF image size info to resized size
    dest_image["Exif.Photo.PixelXDimension"] = image.size[0]
    dest_image["Exif.Photo.PixelYDimension"] = image.size[1]
    dest_image.write(preserve_timestamps=True)
    
    #mtime_tag = dest_image['Exif.Image.DateTime']
    #original_time = mtime_tag.value.strftime('%Y%m%d%H%M.%S')
     
      
for root, dirs, files in os.walk(walk_dir):
	for filename in files:
		jpegs = os.path.join(root, filename)
		if os.path.isfile(jpegs) and re.search('^.*\.jpg$', jpegs, re.I):
			print "Resizing: " + jpegs + " ...",
			outfile = os.path.splitext(jpegs)[0] + ".jpg_resized"
			resize_image(jpegs, outfile, (1920,1920))
		
			# preserve the mtime of destination file	
			st = os.stat(jpegs)
			os.utime(outfile, (st[stat.ST_ATIME], st[stat.ST_MTIME]))
		
			# remove original and rename new file
			os.remove(jpegs)
			os.rename(outfile, jpegs)
			print "Done."
