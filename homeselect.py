#! /bin/python
'''
Created on Ian 23, 2020
@author: petrus.munteanu
''' 

import subprocess

msisdn = raw_input("enter msisdn: ")

try:
    if type (int(msisdn)) == int and int (msisdn) > 0:
        if len(msisdn) == 10:
            pass
        else:
            print("check number of digits")
            quit()
except:
    print('not a corect msisdn')
    quit()

###SQL DATA
connectString = 'database_user/database_pass@database.xxx.domain.intra:1584/stby'
sqlCommand = """set pagesize 999
set linesize 200
select a.* from homezone_subs_opt a, subscribers b where a.id_subscriber = b.id_subscriber and b.msisdn = '""" + msisdn + """';
exit"""
###


def runSqlQuery(sqlCommand, connectString):

    session = subprocess.Popen(['sqlplus64', '-S', connectString], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    (stdout,stderr) = session.communicate(sqlCommand.encode('utf-8'))
    stdout_lines = stdout.decode('utf-8').split("\n")
    return stdout_lines

response = runSqlQuery(sqlCommand, connectString)

for line in response:
    print (line)
