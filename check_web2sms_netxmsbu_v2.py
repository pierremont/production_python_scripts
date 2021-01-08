#! /bin/python

import requests
import time
from datetime import datetime
import sys
import smtplib
import string
import socket
import getpass

url = "https://172.16.xx.xxx/web2sms/index.php"

def send_email(mesaj):
    #SMSBody=mesaj
    SUBJECT = "Alert for docker web2sms"
    TO = "username@domain.com"
    HOSTUSER = getpass.getuser()
    HOSTNAME = socket.gethostname()
    FROM = HOSTUSER + "@" + HOSTNAME
    #text = " \r\n" + SMSBody
    text = " \r\n" + mesaj
    HOST = "localhost"
    BODY = string.join((
        "From: %s" % FROM,
        "To: %s" % TO,
        "Subject: %s" % SUBJECT ,
        "",
        text
        ), "\r\n")
    try:
        server = smtplib.SMTP(HOST)
        server.sendmail(FROM, [TO], BODY)
        server.quit()
    except SMTPException:
        print "Error: unable to send email in " + str(datetime.now()) 

send_email("I've started the stability tests")


#ruleaza 3 zile
for i in range(25920):
    try:
        response = requests.get(url, verify = False)
        if "200" in str(response):
            #print ("am primit 200 OK in " + str(datetime.now()))
            log_file = open("web2sms_stabilitate.txt","a+")
            log_file.write("received 200 ok in " + str(datetime.now()) + "\r\n")
        else:
            eroare_200 = "didn't receive 200 OK in " + str(datetime.now())
            #print eroare_200
            send_email(eroare_200)
            log_file = open("web2sms_stabilitate.txt","a+")
            log_file.write("didn't receive 200 ok in " + str(datetime.now()) + "\r\n")
    except requests.exceptions.ConnectionError as eroare_docker:
        #print "am primit eroare de conexiune de la container in " + str(datetime.now())
        send_email(str(eroare_docker))
        log_file = open("web2sms_stabilitate.txt","a+")
        log_file.write("I've received a communication error from docker in " + str(datetime.now()) + "\r\n")
    except:
        #print "eroare necunoscuta in " + str(datetime.now())
        send_email("unknown error")
        log_file = open("web2sms_stabilitate.txt","a+")
        log_file.write("received an unknown error in " + str(datetime.now()) + "\r\n")
    finally:
        time.sleep(10)

send_email("finished the stability tests for web2sms")