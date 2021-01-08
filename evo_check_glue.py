
import os
import re
import sys

warn=1
max=2
log = "e:/petrus/VAS/howto_technology/devops/devops_scripts/python/testfile3.txt"
ignore_line = "voiceglue httpcache: failure from exec of \"voiceglue_tts_gen -t A serious error has occured.  Exiting. /home/radcom/mediaserver/asterisk/var/lib/asterisk/sounds/voiceglue/tts/nKspH8NWoqCQHdnUbRbm-0c3qQUwqMXJ5_A_serious_error_has_occured___Ex.wav en\": No such file or directory"
response = []

if os.stat(log).st_size != 0:
    file = open(log, "r")
    for line in file:
        if re.search(ignore_line, line):
            status = 0
            statustxt = " Voiceglue OK"
        else:
            status = 2
            statustxt = " Voiceglue errors, MS processes restart recommended (in LifeKeeper); check " + log
    file.close()
else:
    status = 0
    statustxt = " Voiceglue OK"
response.append(str(status) + " Voiceglue_status" + " alarm_status=" + str(status) + ';' + str(warn) + ";" + str(max) + statustxt)
for i in response:
    print i


"""
warn=1
max=2
log=/home/radcom/mediaserver/log/voiceglue_process.log

if [ -s $log ]; then
  status=2
  statustxt="Voiceglue errors, MS processes restart recommended (in LifeKeeper); check $log"
else
  status=0
  statustxt="Voiceglue OK"
fi
echo "$status Voiceglue_status alarm_status=$status;$warn;$max $statustxt"

2 Voiceglue_status alarm_status=2;1;2 Voiceglue errors, MS processes restart recommended (in LifeKeeper); check /home/radcom/mediaserver/log/voiceglue_process.log
"""


