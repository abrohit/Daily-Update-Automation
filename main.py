import requests, datetime, json, os, dotenv
from pytz import timezone

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


def get_siege_update():

    token = os.environ['Siege_Token']
    req = requests.get('https://api.pandascore.co/r6siege/matches/upcoming', params = {'token':token})

    if not req.json(): #api returns empty list if there is no upcoming game
        print('empty')
    else:
        pass
        
    return()

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

       with open('token.pickle', 'wb') as token:
           pickle.dump(creds, token)

   service = build('calendar_token.pickle', 'v3', credentials=creds)
   return(service)

def get_calendar_update():
    
    service = get_calendar_service()

    now = datetime.datetime.now()
    today = now.date()
    current_year = now.year
    
    return()
get_calendar_update()
