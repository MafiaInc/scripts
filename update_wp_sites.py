#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# update_wp_sites.py
#
# This script uses wp-cli <http://wp-cli.org/> to recursively update
# wordpress sites and plugins. It suppose to be ran as root user to
# be able to switch to the user on which the wordpress site belongs to
# before the upgrade.
#
#

#
## Configuration:
base_dir="/usr/local/www"
tag_file="wp-config.php"
wp_cli="/usr/local/bin/wp"

import os, glob, subprocess, sys
from pwd import getpwuid
from grp import getgrgid

def FindInstances(base_dir, tag_file="wp-config.php"):
# Returns list of Wordpress instances as base directory path
# followd by the user and group IDs
   wp = []
   for root, dirs, files in os.walk(base_dir):
      for filename in files:
         if (filename == tag_file):
            try:
               uid = getpwuid(os.stat(os.path.join(root, filename)).st_uid).pw_uid
               gid = getgrgid(os.stat(os.path.join(root, filename)).st_gid).gr_gid
            except:
               print "Unable to retrieve user or group IDs. Please make sure they exists in the system!"
            wp.append([root, uid, gid])
   return wp

def demote(user_id, user_gid):
   """Pass the function 'set_ids' to preexec_fn, rather than just calling
   setuid and setgid. This will change the ids for that subprocess only.
   Thanks to https://gist.github.com/sweenzor/1685717"""
 
   def set_ids():
      os.setgid(user_gid)
      os.setuid(user_id)

   return set_ids

def UpdateWPCore(wp_dir, uid, gid):
# Updates core and DB of the wordpress
   try:
      os.chdir(wp_dir)
   except:
      print "Can't switch to wordpress directory."
 
   UpdateState = []
   
   # Due to the realtime characteristics of the update process output
   # we don't pipe the output of the update, but directly print it 
   wpCore = subprocess.Popen([wp_cli, 'core', 'update'], preexec_fn=demote(uid, gid), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
   for line in iter(wpCore.stdout.readline, ''):
      print line.rstrip()
   wpStdout = wpCore.communicate()
   wpUpdateRC = wpCore.returncode

   if wpUpdateRC: 
      print "Error occured when updating core site in " + wp_dir
   else:
      wpDB = subprocess.Popen([wp_cli, 'core', 'update-db'], preexec_fn=demote(uid, gid), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      DBstdout, DBstderr = wpDB.communicate()
      wpDB_RC = wpDB.returncode
      if wpDB_RC:
         print "Following error occured when updating DB of site " + wp_dir + ":"
         print DBstderr
      UpdateState.append([wpDB_RC, DBstdout])

   UpdateState.append(wpUpdateRC)
   
   return UpdateState

if __name__ == '__main__':

   if os.getuid() is not 0:
      sys.exit("Please run this script as root user!")

   sites = FindInstances(base_dir)
   if not sites: 
      sys.exit('No sites are found!')
   else:
      for instance in sites:
         print "Working with site in: " + instance[0]
         core = UpdateWPCore(instance[0], instance[1], instance[2])
         # print output of WP update-db in case core update was successful
         if core[1] == 0:
            print core[0][1].rstrip()

#TODO: make functions to update also plugins and themes
