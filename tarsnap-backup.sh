#!/bin/sh

TZ=Europe/Sofia
LANG=en_US.UTF-8
TARSNAP_BIN=/usr/local/bin/tarsnap

for dir in $(cat /root/tarsnap-dirs) ; do
        nice $TARSNAP_BIN -c -f $(hostname -s)-$(date -u +%Y%m%d-%H%M%S)-$(echo $dir | tr -d '/') --one-file-system -C / $dir
done
 
#Delete backups more than 10 days old
n=10
$TARSNAP_BIN --list-archives > /tmp/tarsnap-archives.$$ 
if  [ $? != 0 ]; then 
    echo "Error found while listing tarsnap archives! Old archives will not be cleared this time."
    rm /tmp/tarsnap-archives.$$
    break
else
    sort /tmp/tarsnap-archives.$$ | cut -d- -f1-2 | uniq | tail -n $n > /tmp/tarsnap-archives-uniq.$$
    cat /tmp/tarsnap-archives.$$ | fgrep -v -f /tmp/tarsnap-archives-uniq.$$ | while read archive ; do
         echo Deleting $archive
         $TARSNAP_BIN -d -f $archive
    done
    rm /tmp/tarsnap-archives.$$ /tmp/tarsnap-archives-uniq.$$
fi
