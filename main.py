import requests, datetime, json, os, dotenv, smtplib, ssl
from pytz import timezone

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

dotenv_file = os.path.join('.env')
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

def to_ist(Time):

    Time = Time[:-1] #to get rid of Z
    Time_Format = datetime.datetime.strptime(Time, '%H:%M:%S') 

    Diff = 5.5 #IST time difference from UTC

    IST = Time_Format + datetime.timedelta(hours = Diff)

    return(IST.time())

def get_calendar_service():

   SCOPES = ['https://www.googleapis.com/auth/calendar']
   CREDENTIALS_FILE = 'calendar_client_secret.json'
   
   creds = None

   with open('calendar_token.pickle', 'rb') as token:
      creds = pickle.load(token)
      
   if not creds or not creds.valid:
       if creds and creds.expired and creds.refresh_token:
           creds.refresh(Request())
       else:
           flow = InstalledAppFlow.from_client_secrets_file(
               CREDENTIALS_FILE, SCOPES)
           creds = flow.run_local_server(port=0)

       with open('calendar_oken.pickle', 'wb') as token:
           pickle.dump(creds, token)

   service = build('calendar_token.pickle', 'v3', credentials=creds)
   return(service)


def get_siege_update():

    token = os.environ['Siege_Token']
    url = 'https://api.pandascore.co/r6siege/matches/upcoming'
    req = (requests.get(url, params = {'token':token})).json()

    if not req: #api returns empty list if there is no upcoming game

        now = datetime.datetime.now()
        today = now.date()

        #matches = req
        
    else:
        return('')
        
    return('')

def get_f1_update():

    now = datetime.datetime.now()
    today = now.date()
    current_year = now.year

    url = 'https://ergast.com/api/f1/'+ str(current_year)+'.json'
    req = (requests.get(url)).json()
    races = req['MRData']['RaceTable']['Races']#gets data of races for this year

    for item in races:

        race_date = item['date']#gets the date of each race
        
        if today == race_date:
            race = item
        else:
            race=''
            return(race)

        Race_Dets = dict()#creates dict to store race data
        Race_Dets['Round'] = race['round']
        Race_Dets['Race_Name'] = race['raceName']
        Race_Dets['City'] = race['Circuit']['Location']['locality']
        Race_Dets['Country'] = race['Circuit']['Location']['country']

        time = race['time']
        Race_Dets['Time'] = to_ist(time)
    
        return(Race_Dets)

def get_calendar_update():
    
    #service = get_calendar_service()

    now = datetime.datetime.now()
    today = now.date()
    current_year = now.year
    
    return('')

def send_mail(Body):
    
    sender = os.environ['Sender_Email']
    password = os.environ['Sender_Password']
    receiver = os.environ['Receiver_Email']

    smtp_server = "smtp.gmail.com"
    port = 587

    context = ssl.create_default_context()

    try:
        server = smtplib.SMTP(smtp_server,port)
        #server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        #server.ehlo() # Can be omitted
        server.login(sender, password)
        server.sendmail(sender, receiver, Body.as_string())
    except Exception as error:
        print(error)
        server.quit()
    return()

def main():

    email_message = MIMEMultipart("alternative")
    email_message["Subject"] = "Your Daily updates!"

    html_start = """
<html>
  <body>
  <p>Hey,<br>
      Good Morning! This is what your day looks like:<br><br>
"""
    html_end = """
Have a great day!
<p>
</body>
</html>
"""
    html_body = ""
    
    Race_Dets = get_f1_update()
    Siege_Dets = get_siege_update()
    Calendar_Dets = get_calendar_update()

    if Race_Dets != '':
        html_body += "Its race day!! "+ Race_Dets['Race_Name'] + ". This is round "+Race_Dets['Round']+". It's happening at "+ Race_Dets['City']+", " + Race_Dets['Country'] + " at " + str(Race_Dets['Time'])+" IST"+" <br><br>"

    if Siege_Dets != '':
        pass

    if Calendar_Dets != '':
        pass

    if html_body == '':
        html_body += "Looks like you've got nothing happening today! You're free to do whatever you want! Enjoy! <br><br>"

    html = html_start + html_body + html_end

    html_mime = MIMEText(html, "html")
    email_message.attach(html_mime)
    send_mail(email_message)


if __name__ == "__main__": 
    main()

    #https://uhr.rutgers.edu/2020-university-holiday-and-closings-schedule
    
