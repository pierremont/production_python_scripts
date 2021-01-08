#! /usr/local/bin/python2.7
#@author: petrus.munteanu, 2020

###### TABLE OF CONTENTS ######
## import librarii
## parametri configurabili
## connect to email
## SEARCH TODAY'S EMAILS: cautarea emailurilor de azi (incepand cu ora 00) si crearea unei liste (item_list) cu id-urile lor
## fetch today's emails: extragerea emailurilor de azi de pe server si crearea unei liste cu emailurile din ultimele 5 minute
## check the log file: check in log ca sa filtram emailurile deja procesate si cream o lista de id-uri (email_to_process) cu cele ramase (neprocesate)
## function: check_sender entitlement
## function: send_email, petru reply to sender
## function: write_log, scrie in log
## function: get_text, aduce email body
## FOR: extract again the emails from the server, but only the emails that need to be processed (filtered above), adica lista email_to_process. Aici e logica principala care proceseaza mailurile, pe rand (intr-un FOR):
    ## adapteaza campurile din mail, pentru scrierea lor in log
    ## scrie campurile in log (function: write in the processing log)
    ## verifica user si group entitlement (function: check_sender)
    ## cauta primele 3 linii din email body si le scrie in log (password=, type=, prefix=)
    ## IF type=select_routes -> trigger scriptul din acelasi folder: oasis_child_itr_select.itr_select(prefix)
    ## IF type=select_carriers -> trigger scriptul din acelasi folder: oasis_child_itr_select.itr_carriers
    ##...............
    ## assemble reply body: in functie de type si raspunsul de la scriptul extern, formuleaza reply-ul si cheama functia send_email
## mail.close()
## mail.logout()
## quit()


############################
import imaplib
import email
from datetime import datetime

############################
### CONFIGURABLE PARAMETERS
vas_authorized_users =['user@domain.com','user2@domain.com']
vas_password = 'vas_pass'
vas_access = ['select_routes','update_main_routes', 'select_carriers', 'select_homezone', 'update_homezone', 'update_transit_routes', 'update_notransit_directtraffic_routes', 'update_second_routes', 'update_third_routes']

smc_authorized_users = []
smc_password = 'smc_pass'
smc_access = ['select_routes', 'update_main_routes', 'select_carriers', 'update_transit_routes', 'update_notransit_directtraffic_routes', 'update_second_routes', 'update_third_routes']


default_CC = ["user@domain.com"]
##default_CC = ["team@domain.com"]


###########################
### CONNECT TO EMAIL
imap_url = 'mail.domain.ro'
user = 'email_user'
password = 'pass'

mail = imaplib.IMAP4_SSL(imap_url, 993)  # connect
mail.login(user, password)  # login


##########################
### SEARCH TODAY'S EMAILS:
#print(mail.list())     #prints the inbox folders
mail.select('Oasis_prov_requests')
#result, data = mail.uid('search', None, "ALL")  # search all emails. For unread emails use UNSEEN instead of ALL
#result, data = mail.uid('search','(SUBJECT "oasis_itr_request" SINCE "03-Apr-2020")')

    # search with timedelta the emails from today
import datetime
date = (datetime.datetime.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
(result, data) = mail.uid('search', '(SUBJECT {0})'.format('oasis_prov_request'), '(SINCE {0})'.format(date))

# '(SENTSINCE {0})'.format(date)), '(FROM {0})'.format("someone@yahoo.com".strip()))

item_list = data[0].split()  # turn the output into a list
#print item_list   #all the emails uids from search, in a list


########################
### FETCH TODAY'S EMAILS
if len(item_list) == 0: #if there's no email found, the fetch outputs an error, so we need to check for this
    mail.close()
    mail.logout()
    quit()  #if there are no emails today
else:
    pass

last_5minutes_uids = []
for i in item_list:
    result2, email_data = mail.uid('fetch', i, 'RFC822')  # newest email, in bytes, as a tuple
    raw_email = email_data[0][1]
    # raw_email = email_data[0][1].decode("utf-8")    #only for python 3 - decode the email from bytes to utf
    email_message = email.message_from_string(raw_email)  # turns the message into an object
    from datetime import datetime

    #check the email date in order to take only the last 5 minutes emails
    email_date = datetime.strptime(email_message['Date'], '%a, %d %b %Y %H:%M:%S +%f')  # converts it to datetime type
    now = datetime.now()
    difference = int(((now - email_date).total_seconds()) / 60)

    #attach the last 5 minutes emails to a list
    if difference > 10:   ##the interval in minutes in which the script will search
        pass
    else:
        last_5minutes_uids.append(i)
#print (last_5minutes_uids)


#######################
### CHECK THE LOG FILE, to see if the emails have already been processed
if len(last_5minutes_uids) == 0: #if there's no email found in the last 5 minutes, the log search below outputs an error, so we need to check for this
    mail.close()
    mail.logout()
    quit()      #if there are no emails today
else:
    pass

import re
file = open("/root/oasis_provisioning_bot/oasis_log.txt", "r")
email_to_process = []
for mail_uid in last_5minutes_uids:
    found = 0
    for line in file:
        search_text = ("mail_uid:" + mail_uid)
        if re.search(search_text, line):
            found = 1
            break
    if found == 0:
        email_to_process.append(mail_uid)

if len(email_to_process) == 0: #if all the emails were already written in the log
    #print("all the emails were in the log")
    mail.close()
    mail.logout()
    quit()
else:
    pass
file.close()


##########################
### FUNCTION: CHECK_SENDER entitlement
def check_sender(current_sender, current_password):
    if current_sender in vas_authorized_users and current_password==vas_password:
        sender_auth = "authorized"
        sender_access = vas_access
    elif current_sender in smc_authorized_users and current_password==smc_password:
        sender_auth = "authorized"
        sender_access = smc_access
    else:
        sender_auth = "not_authorized"
    return sender_auth, sender_access
    
    
########################
### FUNCTION: SEND_EMAIL, in order to reply to sender
import smtplib
import string
import socket
import getpass

def send_email(current_subject, current_sender, reply_message):
    SUBJECT = "RE: " + current_subject
    TO = current_sender
    HOSTUSER = getpass.getuser()
    HOSTNAME = socket.gethostname()
    FROM = HOSTUSER + "@" + HOSTNAME
    text = " \r\n" + reply_message
    HOST = "localhost"
    BODY = string.join((
        "From: %s" % FROM,
        "To: %s" % TO,
        "Cc: %s" % ",".join(reply_CC),
        "Subject: %s" % SUBJECT ,
        "",
        text
        ), "\r\n")
    try:
        server = smtplib.SMTP(HOST)
        server.sendmail(FROM, [TO], BODY)
        server.quit()
    except:
        print "Error: unable to send email in " + str(datetime.now())
        
        
########################
### FUNCTION: WRITE_LOG, writes details about the emails in the processing log
def write_log(log_record):
    log_file = ("/root/oasis_provisioning_bot/oasis_log.txt")
    f = open(log_file,"a+")
    f.write(log_record + " \n")

    f.close()


#########################
### FUNCTION: GET_TEXT - fetch email body, it only works for the emails sent in text format
def get_text(msg):
    if email_message.is_multipart():
        return get_text(email_message.get_payload(0))
    else:
        return email_message.get_payload(None, True)
        
        
###########################
## EXTRACT AGAIN THE EMAILS FROM THE SERVER AND TRIGGER EXTERNAL SCRIPTS, but only for the emails that need to be processed (filtered in the CHECK THE LOG FILE section):
for i in email_to_process:
    result2, email_data = mail.uid('fetch', i, 'RFC822')  # newest email, in bytes, as a tuple
    raw_email = email_data[0][1]
    # raw_email = email_data[0][1].decode("utf-8")    #only for python 3 - decode the email from bytes to utf
    email_message = email.message_from_string(raw_email)  # turns the message into an object

    email_date = email_message['Date']

    current_sender = email_message['From'].split("<")  # separates the nickname
    current_sender = current_sender[1].lower().strip(">")  # converts to lowercase and removes the last particle
    current_date = datetime.strptime(email_message['Date'], '%a, %d %b %Y %H:%M:%S +%f')  # converts it to datetime type
    current_date_for_reply = current_date.strftime("%A, %B %d, %Y %I:%M %p")
    current_date = current_date.strftime("%d %b %Y %H:%M:%S")
    current_subject = email_message['Subject']
    
    ## trying to catch the CC
    reply_CC = default_CC    #reinitialize the cc list after each processed email
    if email_message['Cc']:          ## if there are people in Cc (value not null)
        lista_cc = email_message['Cc'].split(",")
        for i in lista_cc:
            #print("cc = " + i + "\n")
            original_current_cc = i.split("<")
            original_current_cc = original_current_cc[1].lower().strip(">")
            reply_CC.append(original_current_cc)
        print(reply_CC)
    else:
        print("nothing in Cc")
    # new_cc = []
    
        # for i in email_message['Cc']:
            # current_cc = i.split("<")  # separates the nickname
            # print(current_cc)
            # # current_cc = current_cc[1].lower().strip(">")  # converts to lowercase and removes the last particle
            # new_cc.append(current_cc)
        # print(new_cc)
    
    log_record = ("mail_uid:" + i + " | " + current_sender + " | " + email_message['Subject'] + " | " + current_date)
    write_log("##################################" + "\n" + log_record)
    
    email_body = get_text(email_message)
    body_line = email_body.split("\n")
    current_password = body_line[0].split("=")
    current_password = current_password[1].strip()
    
    ## check user entitlement
    sender_auth, sender_access = check_sender(current_sender, current_password)
    print(sender_auth)

    if sender_auth == 'authorized':
        write_log("user authorized" + "\n")
    else:
        write_log("user not accepted, wrong password sent or mail format is not text" + "\n")
        quit()

    write_log(body_line[0] + "\n" + body_line[1] + "\n")    ##this should be adapted in order to write the first 4 lines of the mail in the log. Right now it crashes if there's no third or 4th row


    ################### main brain ##########################
    #########################################################
    if re.search("type=select_routes", body_line[1].lower()):
        prefix = body_line[2].split("=")
        type = body_line[1].split("=")
        type = str(type[1]).strip()
        print(type)
        if type.lower() not in sender_access:   # check if the group has access to this type
            write_log("group not authorized" + "\n")
            script_result_final = "unfortunately your group doesnt have access to this type"
        else:
            print "ok, trigger outside script"
            prefix = str(prefix[1].strip())
            import oasis_child_itr_select
            found_routes, carriers = oasis_child_itr_select.select_routes(prefix)  #trigger the child script
            script_result_final = ""
            for line in found_routes:
                script_result_final = script_result_final + str(line) + "\n"
            for line in carriers:
                script_result_final = script_result_final + str(line) + "\n"
            print(script_result_final)
            # script_result = "".join(script_result) #converts the list into unicode/string variable, in order to add it to the reply
    ########################################
      
    ########################################      
    elif re.search("type=update_main_routes", body_line[1].lower()):
        prefix = body_line[2].split("=")
        new_carrier=body_line[3].split("=")
        type = body_line[1].split("=")
        type = str(type[1]).strip()
        print(type)
        if type.lower() not in sender_access:   # check if the group has access to this type
            write_log("group not authorized" + "\n")
            script_result_final = "unfortunately your group doesnt have access to this type"
        else:
            print "ok, trigger outside script"
            prefix = str(prefix[1].strip())
            new_carrier=str(new_carrier[1].strip())
            import oasis_child_itr_main_update
            routes_before, routes_after = oasis_child_itr_main_update.main_update(prefix, new_carrier) #trigger the child script
            script_result_final = ""
            for line in routes_after:
                script_result_final= script_result_final + str(line) + "\n"
            for line in routes_before:
                script_result_final = script_result_final + str(line) + "\n"
            print(script_result_final)
            # script_result = "".join(script_result)   #converts the list into unicode/string variable, in order to add it to the reply
    #######################################
    
    ########################################      
    elif re.search("type=update_second_routes", body_line[1].lower()):
        prefix = body_line[2].split("=")
        new_carrier=body_line[3].split("=")
        type = body_line[1].split("=")
        type = str(type[1]).strip()
        print(type)
        if type.lower() not in sender_access:   # check if the group has access to this type
            write_log("group not authorized" + "\n")
            script_result_final = "unfortunately your group doesnt have access to this type"
        else:
            print "ok, trigger outside script"
            prefix = str(prefix[1].strip())
            new_carrier=str(new_carrier[1].strip())
            import oasis_child_itr_second_update
            routes_before, routes_after = oasis_child_itr_second_update.second_update(prefix, new_carrier) #trigger the child script
            script_result_final = ""
            for line in routes_after:
                script_result_final= script_result_final + str(line) + "\n"
            for line in routes_before:
                script_result_final = script_result_final + str(line) + "\n"
            print(script_result_final)
            # script_result = "".join(script_result)   #converts the list into unicode/string variable, in order to add it to the reply
    #######################################
    
    ########################################      
    elif re.search("type=update_third_routes", body_line[1].lower()):
        prefix = body_line[2].split("=")
        new_carrier=body_line[3].split("=")
        type = body_line[1].split("=")
        type = str(type[1]).strip()
        print(type)
        if type.lower() not in sender_access:   # check if the group has access to this type
            write_log("group not authorized" + "\n")
            script_result_final = "unfortunately your group doesnt have access to this type"
        else:
            print "ok, trigger outside script"
            prefix = str(prefix[1].strip())
            new_carrier=str(new_carrier[1].strip())
            import oasis_child_itr_third_update
            routes_before, routes_after = oasis_child_itr_third_update.third_update(prefix, new_carrier) #trigger the child script
            script_result_final = ""
            for line in routes_after:
                script_result_final= script_result_final + str(line) + "\n"
            for line in routes_before:
                script_result_final = script_result_final + str(line) + "\n"
            print(script_result_final)
            # script_result = "".join(script_result)   #converts the list into unicode/string variable, in order to add it to the reply
    #######################################
    
    ########################################      
    elif re.search("type=update_transit_routes", body_line[1].lower()):
        prefix = body_line[2].split("=")
        new_carrier=body_line[3].split("=")
        type = body_line[1].split("=")
        type = str(type[1]).strip()
        print(type)
        if type.lower() not in sender_access:   # check if the group has access to this type
            write_log("group not authorized" + "\n")
            script_result_final = "unfortunately your group doesnt have access to this type"
        else:
            print "ok, trigger outside script"
            prefix = str(prefix[1].strip())
            new_carrier=str(new_carrier[1].strip())
            import oasis_child_itr_transit_update
            routes_before, routes_after = oasis_child_itr_transit_update.transit_update(prefix, new_carrier) #trigger the child script
            script_result_final = ""
            for line in routes_after:
                script_result_final= script_result_final + str(line) + "\n"
            for line in routes_before:
                script_result_final = script_result_final + str(line) + "\n"
            print(script_result_final)
            # script_result = "".join(script_result)   #converts the list into unicode/string variable, in order to add it to the reply
    #######################################
    
    ########################################      
    elif re.search("type=update_notransit_directtraffic_routes", body_line[1].lower()):
        prefix = body_line[2].split("=")
        new_carrier=body_line[3].split("=")
        type = body_line[1].split("=")
        type = str(type[1]).strip()
        print(type)
        if type.lower() not in sender_access:   # check if the group has access to this type
            write_log("group not authorized" + "\n")
            script_result_final = "unfortunately your group doesnt have access to this type"
        else:
            print "ok, trigger outside script"
            prefix = str(prefix[1].strip())
            new_carrier=str(new_carrier[1].strip())
            import oasis_child_itr_notransit_directtraffic_update
            routes_before, routes_after = oasis_child_itr_notransit_directtraffic_update.notransit_update(prefix, new_carrier) #trigger the child script
            script_result_final = ""
            for line in routes_after:
                script_result_final= script_result_final + str(line) + "\n"
            for line in routes_before:
                script_result_final = script_result_final + str(line) + "\n"
            print(script_result_final)
            # script_result = "".join(script_result)   #converts the list into unicode/string variable, in order to add it to the reply
    #######################################
            
    #######################################    
    elif re.search("type=select_carriers", body_line[1].lower()):
        type = body_line[1].split("=")
        type = str(type[1]).strip()
        print(type)
        if type.lower() not in sender_access:   # check if the group has access to this type
            write_log("group not authorized" + "\n")
            script_result_final = "unfortunately your group doesnt have access to this type"
        else:
            print "ok, trigger outside script"
            import oasis_child_itr_carriers
            script_result = oasis_child_itr_carriers.carriers_select()   #trigger the child script
            script_result_final = ""
            for line in script_result:
                script_result_final = script_result_final + str(line) + "\n"
    #######################################
    
    #######################################    
    elif re.search("type=select_homezone", body_line[1].lower()):
        msisdn = body_line[2].split("=")
        type = body_line[1].split("=")
        type = str(type[1]).strip()
        print(type)
        if type.lower() not in sender_access:   # check if the group has access to this type
            write_log("group not authorized" + "\n")
            script_result_final = "unfortunately your group does not have access to this type"
        else:
            print "ok, trigger outside script"
            msisdn = str(msisdn[1].strip())
            import oasis_child_homezone_select
            homezone = oasis_child_homezone_select.homezone_select(msisdn)    #trigger the child script
            script_result_final = ""
            for line in homezone:
                script_result_final = script_result_final + str(line) + "\n"
    #####################################

    ########################################      
    elif re.search("type=update_homezone", body_line[1].lower()):
        msisdn = body_line[2].split("=")
        radius=body_line[3].split("=")
        type = body_line[1].split("=")
        type = str(type[1]).strip()
        print(type)
        if type.lower() not in sender_access:   # check if the group has access to this type
            write_log("group not authorized" + "\n")
            script_result_final = "unfortunately your group doesnt have access to this type"
        else:
            print "ok, trigger outside script"
            msisdn = str(msisdn[1].strip())
            radius=str(radius[1].strip())
            import oasis_child_homezone_update
            homezone_before, homezone_after = oasis_child_homezone_update.homezone_update(msisdn, radius) #trigger the child script
            script_result_final = ""
            for line in homezone_after:
                script_result_final= script_result_final + str(line) + "\n"
            for line in homezone_before:
                script_result_final = script_result_final + str(line) + "\n"
            print(script_result_final)
            # script_result = "".join(script_result)   #converts the list into unicode/string variable, in order to add it to the reply
    #######################################    
    
    #####################################  
    else:
        print("there was no clear select or update on the second line")   #reply to sender with reject
        script_result_final = "there was no clear select or update on the second line, or the email format is not text"
    #####################################
    
    print ("================================")
    
    #####################################
    ### assemble reply body
    reply_message = script_result_final + "\n" + "\n" + "From: " + current_sender + "\n" + "Sent: " + current_date_for_reply + "\n" + "To: vasmon@domain.com" + "\n" + "Subject: " + current_subject + "\n" + email_body

    send_email(current_subject, current_sender, reply_message) 
    write_log("reply sent" + "\n")
  

###################################################



mail.close()
mail.logout()
quit()



'''
##### fetch last email, used only for testing:
newest_item = item_list[-1]        #newest_email uid
# oldest_item = item_list[0]      #oldest_email

result2, email_data = mail.uid('fetch', newest_item, 'RFC822')  # fetched newest email by uid, in bytes, as a tuple
raw_email = email_data[0][1]
# raw_email = email_data[0][1].decode("utf-8")    #only for python 3 - decode the email from bytes to utf
email_message = email.message_from_string(raw_email)  # turns the message into an object
# print(dir(email_message))   #prints out the functions available for the object
current_date = email_message['Date']
current_sender = email_message['From'].split("<")   #separates the nickname
current_sender = current_sender[1].lower().strip(">") #converts to lowercase and removes the last particle
log_record = ("mail_uid:" + newest_item + " | " + current_sender + " | " + email_message['Subject'] + " | " + email_message['Date'])
print (log_record)
##################
'''



