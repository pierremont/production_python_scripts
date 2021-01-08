#! /usr/local/bin/python2.7
    
#@author: petrus.munteanu, 2020

def homezone_update(msisdn, radius):    
    import subprocess
    homezone_before = []
    homezone_after = []
    
    ############################
    ### CHECK THE INPUT DATA
    
    ### check if the msisdn has a number format and is positive ######
    try:
         if type (int(msisdn)) == int and int (msisdn) > 0:
            if len(msisdn) == 10:
                pass
    except:
        homezone_before.append('not a correct msisdn')
        return homezone_before, homezone_after ## this will terminate the function
        
        
    ### check the new radius format
    try:
        if type (int(radius)) == int and int (radius) > 0:
            pass
        else:
            print
            print("not a correct radius!")
            homezone_before.append('not a correct radius!')
            return homezone_before, homezone_after ## this will terminate the function
    except:
        print
        print('not a corect radius')
        homezone_before.append('not a correct radius!')
        return homezone_before, homezone_after ## this will terminate the function
        quit()
        
    ###########################
    ## RETURN THE SETTINGS BEFORE THE UPDATE
    
    def runSqlQuery(qlCommand, connectString):

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

    ### check for home option
    response = runSqlQuery(sqlCommand, connectString)
    for line in response:
        if line == "home_data":
            print ("subscriber doesn't have the home option active, but has home_data (check the provisioning flow))")
            homezone_before.append("subscriber doesn't have the home option active, but has home_data (check the provisioning flow)")
            return homezone_before, homezone_after ## this will terminate the function
            quit()
        elif line == "no rows selected":
            print ("subscriber doesn't have any active option (check the provisioning flow)")
            homezone_before.append("subscriber doesn't have any active option (check the provisioning flow)")
            return homezone_before, homezone_after ## this will terminate the function
            quit()
        else:
            pass
   
    ### return the settings
    ###SQL DATA
    connectString = 'oasis/RADcom_00@oasisstbydb-billing.crm.orange.intra:1584/oasisstby'
    sqlCommand = """set pagesize 999;
    set linesize 300;
    set heading off;
    column start_date format a22 heading start_date justify center;
    column end_date format a20 heading end_date  justify center;
    column zone_status format a18 justify center;
    column msisdn format a15 heading msisdn justify center;
    select msisdn, zone_status as status, radius, lac, ci, x, y, name, end_date from homezone_subs_opt a, subscribers b where a.id_subscriber = b.id_subscriber and b.msisdn = '""" + msisdn + """';
    exit"""
    ###    
    homezone_before = runSqlQuery(sqlCommand, connectString)
    homezone_before.insert(0,"   MSISDN      " + "    ZONE_STATUS   " + "  RADIUS    " + "  LAC      " + "    CI     " + "      X            " + "    y     " +  "     NAME               " + "                      END_DATE   ")
    homezone_before.insert(0, ("the old settings for msisdn " + str(msisdn) + ":" + "\n"))
    homezone_before.insert(0, ("\n" + "#################################"))
    #############################
    
    
    ############################
    ### UPDATE THE RADIUS
    print("updated home radius for msisdn " + str(msisdn) + ":")
    ###SQL DATA
    connectString = 'oasis/RADcom_00@oasisstbydb-billing.crm.orange.intra:1584/oasisstby'
    sqlCommand = """set pagesize 999
    set linesize 200
    update homezone_subs_opt set radius = """ + radius + """ where id_subscriber= (select id_subscriber from subscribers where msisdn = '""" + msisdn + """') and name = 'home'; 
    commit ;
    exit"""
    ###
    
    response = runSqlQuery(sqlCommand, connectString)
    for line in response:
        print (line)
    
    
    #########################
    ###SQL DATA
    connectString = 'oasis/RADcom_00@oasisstbydb-billing.crm.orange.intra:1584/oasisstby'
    sqlCommand = """set pagesize 999;
    set linesize 300;
    set heading off;
    column start_date format a22 heading start_date justify center;
    column end_date format a20 heading end_date  justify center;
    column zone_status format a18 justify center;
    column msisdn format a15 heading msisdn justify center;
    select msisdn, zone_status as status, radius, lac, ci, x, y, name, end_date from homezone_subs_opt a, subscribers b where a.id_subscriber = b.id_subscriber and b.msisdn = '""" + msisdn + """';
    exit"""
    ###  
    
    # response2 = runSqlQuery(sqlCommand, connectString)
    # for line in response2:
        # print (line)
        
    homezone_after = runSqlQuery(sqlCommand, connectString)
    homezone_after.insert(0,"   MSISDN      " + "    ZONE_STATUS   " + "  RADIUS    " + "  LAC      " + "    CI     " + "      X            " + "    y       " +  "     NAME             " + "                      END_DATE   ")
    homezone_after.insert(0, ("new settings for msisdn " + str(msisdn) + ":"))
    return homezone_before, homezone_after
    
        
# msisdn = '447407'
# homezone_before, homezone_after = main_update(msisdn, new_carrier)

# for line in homezone_before:
    # print(line)
# for line in homezone_after:
    # print(line)
    
    