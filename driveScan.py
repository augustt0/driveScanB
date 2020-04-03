from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from datetime import datetime
import time
import threading

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config

print("Loaded emails: AT SEND TIME")

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
nService = None

date = datetime.utcnow()

def main():
    global nService
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    nService = service
    scanForFiles()
 
def sendEmails(trabajosPracticos):
    f = open('listaEmails.txt', 'r')
    x = f.readlines()
    listaEmails = ",".join(x)
    mail_content = config.mail_content
    mail_content = mail_content + trabajosPracticos
    #The mail addresses and password
    sender_address = config.my_email
    sender_pass = config.gmail_pass
    receiver_address = listaEmails
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = config.subject   #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Emails correctly sended to: ')
    print(listaEmails)

def scanForFiles():
    global date
    listaTPS = ""
    threading.Timer(10.0, scanForFiles).start()
    print("Checkeando archivos creados despues de: {}".format(date.isoformat()))
    results = nService.files().list(q="modifiedTime>= '{}' and '{}' in parents".format(date.isoformat(), config.folder_id)).execute()
    #TEST ONLY results = nService.files().list(q="modifiedTime>= '{}'".format(date.isoformat())).execute()
    items = results.get('files', [])
    if not items:
        print("There were no new files")
    else:
        date = datetime.utcnow()
        print("There were new files: ")
        for tp in items:
            print(tp['name'])
            listaTPS = listaTPS + "\r\n" + tp['name'] + ": https://drive.google.com/file/d/" + tp['id'] + "/view \r\n"
        sendEmails(listaTPS)

if __name__ == '__main__':
    main()