#! /bin/python
'''
Created on Ian 23, 2020
@author: petrus.munteanu
'''
import subprocess

##### get the msisdn
msisdn = raw_input("enter msisdn: ")
try:
    if type (int(msisdn)) == int and int (msisdn) > 0:
        if len(msisdn) == 10:
            pass
        else:
            print
            print("check number of digits")
            quit()
except:
    print('not a corect msisdn')
    quit()


##### define the sql function
def runSqlQuery(sqlCommand, connectString):

    session = subprocess.Popen(['sqlplus64', '-S', connectString], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    (stdout,stderr) = session.communicate(sqlCommand.encode('utf-8'))
    stdout_lines = stdout.decode('utf-8').split("\n")
    return stdout_lines


##### check for home option (data option will not be processed)
print ("checking option for msisdn " + str(msisdn) + ":")
###SQL DATA
connectString = 'user/pass@databse.xxx.domain.intra:1584/stby'
sqlCommand = """set pagesize 999
set linesize 200
select name from homezone_subs_opt where id_subscriber = (select id_subscriber from subscribers where msisdn = '""" + msisdn + """');
exit"""


response = runSqlQuery(sqlCommand, connectString)
for line in response:
    if line == "home_data":
        print ("subscriber doesn't have the home option active, but has home_data (check the provisioning flow))")
        quit()
    elif line == "no rows selected":
        print ("subscriber doesn't have any active option (check the provisioning flow)")
        quit()
    else:
        pass
#######



##### print current settings
print ("current settings for msisdn " + str(msisdn) + ":")
###SQL DATA
connectString = 'user/pass@databse.xxx.domain.intra:1584/stby'
sqlCommand = """set pagesize 999
set linesize 200
select a.* from homezone_subs_opt a, subscribers b where a.id_subscriber = b.id_subscriber and b.msisdn = '""" + msisdn + """';
exit"""
###

response = runSqlQuery(sqlCommand, connectString)
for line in response:
    print (line)

print
print

###### get the radius
radius = raw_input("enter radius in meters: ")
try:
    if type (int(radius)) == int and int (radius) > 0:
        pass
    else:
        print
        print("not a correct radius!")
except:
    print
    print('not a corect radius')
    quit()

print
print

##### update the radius
print("updated home radius for msisdn " + str(msisdn) + ":")
###SQL DATA
connectString = 'user/pass@databse.xxx.domain.intra:1584/stby'
sqlCommand = """set pagesize 999
set linesize 200
update homezone_subs_opt set radius = """ + radius + """ where id_subscriber= (select id_subscriber from subscribers where msisdn = '""" + msisdn + """') and name = 'home'; 
commit ;
select a.* from homezone_subs_opt a, subscribers b where a.id_subscriber = b.id_subscriber and b.msisdn = '""" + msisdn + """';
exit"""
###

response = runSqlQuery(sqlCommand, connectString)
for line in response:
    print (line)









