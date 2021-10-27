import requests,boto3,re,os
from datetime import datetime,timedelta
from os.path import join, dirname
from dotenv import load_dotenv

client = boto3.client('ce', region_name='us-east-1')
dotenv_path = join(dirname(__file__), '.env')

# 合計請求額を取得
def get_cost(client) -> dict:
    
    start = datetime.now().replace(day=1).strftime('%F')
    end = datetime.now().strftime('%F')

    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start,
            'End': end,
        },
        Granularity='MONTHLY',
        Metrics=[
            'AmortizedCost'
        ]
    )

    return {
        'start': response['ResultsByTime'][0]['TimePeriod']['Start'],
        'end': response['ResultsByTime'][0]['TimePeriod']['End'],
        'billing': response['ResultsByTime'][0]['Total']['AmortizedCost']['Amount'],
    }

def calc_exchange():

    date = get_cost(client)
    
    #get exchange yen-dollar
    exchange = requests.get('https://www.gaitameonline.com/rateaj/getrate').json()['quotes'][20]['open']
    total =  float(exchange)*float(date['billing'])

    pattern = "(\d+).(\d+)"
    d = re.search(pattern, str(total))
    
    return f"({date['start']}から{date['end']}の利用料金は{d.group(1)}円です)"

# LINEに通知
def send_message():

    load_dotenv(dotenv_path)
    token = os.environ["LINE_token"]

    headers = {
        'Authorization':token,
    }
    
    text = calc_exchange()
    
    files = {
        'message': (None,text),
    }
    
    requests.post('https://notify-api.line.me/api/notify', headers=headers, files=files)
    
send_message()