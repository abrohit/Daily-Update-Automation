import requests, datetime, json, os, dotenv
from pytz import timezone

dotenv_file = os.path.join('.env')
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

def to_ist(Time):

    Time = Time[:-1]
    Time_Format = datetime.datetime.strptime(Time, '%H:%M:%S')

    Diff = 5.5

    IST = Time_Format + datetime.timedelta(hours = Diff)

    return(IST.time())


def get_siege_update():

    token = os.environ['Siege_Token']
    req = requests.get('https://api.pandascore.co/r6siege/matches/upcoming', params = {'token':token})

    if not req.json():
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
    races = req['MRData']['RaceTable']['Races']

    for item in races:

        race_date = item['date']
        
        if today == race_date:
            race = item
        else:
            race=''
            return(race)

        Race_Dets = dict()
        Race_Dets['Round'] = race['round']
        Race_Dets['Race_Name'] = race['raceName']
        Race_Dets['Place'] = race['Circuit']['Location']['locality'] + ', ' + race['Circuit']['Location']['country']

        time = race['time']
        Race_Dets['Time'] = to_ist(time)
    
        return(Race_Dets)

def get_calendar_update():
    return()

