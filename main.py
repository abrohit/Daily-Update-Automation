import requests, datetime, json, os, dotenv, smtplib, ssl

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

dotenv_file = os.path.join('.env')
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

def to_ist(Time):

    Time = Time[:-1] #to get rid of Z
    Time_Format = datetime.datetime.strptime(Time, '%H:%M:%S') 

    Diff = 5.5 #IST time difference from UTC

    IST = Time_Format + datetime.timedelta(hours = Diff)
    return(IST.time())

def get_uni_schedule():

    now = datetime.datetime.now()
    day = str(now.strftime("%A"))

    with open('Timetable.json') as f:
        data = json.load(f)

    try:
        return(data[day])
    except KeyError: # Will return KeyError when it's Sunday or Saturday
        return('')

def get_uni_holidays():

    now = datetime.datetime.now()
    current_year = str(now.year)

    day = str(now.strftime("%A")) # Gets the current day of the week, example: Monday, Tuesday...
    month = str(now.strftime('%B'))# Gets the current month, example: August, October....
    date = (str(now.date()).split('-'))[2] # Gets only the Date, example: 1 or 2 or 23

    today = day + ', ' + month + ' ' + date + ', ' + current_year
    
    url = 'https://uhr.rutgers.edu/'+current_year+'-university-holiday-and-closings-schedule'
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    sauce = urlopen(req).read()
    soup=BeautifulSoup(sauce,'lxml')

    table=soup.find('table')
    table_rows = table.find_all('tr')

    for item in table_rows:
        td = item.find_all('td')
        row = ([i.text for i in td])
        if row[1] == today:
            return(row[0])

    return('')


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

    Team_to_follow = "G2 Esports"

    token = os.environ['Siege_Token']
    url = 'https://api.pandascore.co/r6siege/matches/upcoming'
    req = (requests.get(url, params = {'token':token})).json()
    
    if req: #api returns empty list if there is no upcoming game
        
        now = datetime.datetime.now()
        today = now.date()
        
        for item in req:
            
            match_scheduled = (item['scheduled_at']).split("T")#splits time and date
            match_date = match_scheduled[0]
            
            if today == match_date:#checks if there is a game today

                teams_data = item['opponents']
                team_names = []
                
                for item_two in teams_data:
                    team_names.append(item_two['opponent']['name'])#gets the name of both teams playing today

                if (Team_to_follow in team_names):#checks if your favourite team is playing today

                    Game_Dets = dict()

                    Game_Dets['League_Name'] = item['league']['slug']
                    Game_Dets['Match_Name'] = item['name']
                    Game_Dets['Time'] = str(to_ist(match_scheduled[1]))

                    return(Game_Dets)

            else:
                return('')
    else:
        return('')

def get_f1_update():

    now = datetime.datetime.now()
    today = str(now.date())
    current_year = now.year

    url = 'https://ergast.com/api/f1/'+ str(current_year)+'.json'
    req = (requests.get(url)).json()
    races = req['MRData']['RaceTable']['Races']#gets data of races for this year

    race = ''

    for item in races:

        race_date = item['date']#gets the date of each race
        
        if today == race_date:
            race = item

    if race != '':
        
        Race_Dets = dict()#creates dict to store race data
        Race_Dets['Round'] = race['round']
        Race_Dets['Race_Name'] = race['raceName']
        Race_Dets['City'] = race['Circuit']['Location']['locality']
        Race_Dets['Country'] = race['Circuit']['Location']['country']
        Race_Dets['Time'] = str(to_ist(race['time']))
        
        return(Race_Dets)
    
    else:
        
        return(race)

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
    Holiday_Dets = get_uni_holidays()
    Schedule_Dets = get_uni_schedule()

    if Holiday_Dets != '':
        html_body += "Today is a Holiday!!! It's " + Holiday_Dets + "!!!" + " <br><br>"

    if Schedule_Dets != '' and Holiday_Dets == '':

        html_body += "You have these classes lined up for the day: <br><ul>"

        for item in Schedule_Dets:
            html_body += "<li>" + str(item) + " at " + str(Schedule_Dets[item])+"</li>"
        html_body += "</ul><br>"

    if Race_Dets != '':
        html_body += "Its race day!! "+ Race_Dets['Race_Name'] + ". This is round "+Race_Dets['Round']+". It's happening at "+ Race_Dets['City']+", " + Race_Dets['Country'] + " at " + str(Race_Dets['Time'])+" IST"+" <br><br>"

    if Siege_Dets != '':
        html_body += "It's Siege day!! It's time for "+ Siege_Dets['League_Name'] + ". " + Siege_Dets['Match_Name'] + " at " + Siege_Dets['Time'] + " IST" + " <br><br>"

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
