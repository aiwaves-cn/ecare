import os
import json
import requests
from langchain.agents import tool
import datetime
import time
import pytz
from langchain_core.pydantic_v1 import BaseModel, Field

from  contextvars import ContextVar

TZ = pytz.timezone('Asia/Shanghai')
HEADERS = {'Content-Type': 'application/json'}
@tool
def get_current_time():
    """获取当前的时间"""
    count = 0
    url = 'https://api.wizpathonline.com:50443/openApi/api/time/current'
    while count < 3:
        response = requests.request('GET', url)
        if response.status_code == 200:
            break
        else:
            count += 1
    if count == 3:
        timestamp = datatime.now()
    else:
        response = response.json()
        timestamp = response['data']
    timestamp_in_seconds = timestamp / 1000
    date_time = datetime.datetime.fromtimestamp(timestamp_in_seconds)   
    formatted_date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_date_time

class WeatherInput(BaseModel):
    address: str =Field(..., description='查询天气的地理位置')

@tool(args_schema = WeatherInput)
def get_location_weather(weatherinput: WeatherInput):
    """获取指定位置的天气"""
    count = 0
    url = "https://api.wizpathonline.com:50443/openApi/api/weather/query"
    data = json.dumps({"address":weatherinput.address})
    while count < 3:
        response = requests.request('POST', url, headers=HEADERS, data=data)
        print(response,url,response.json())
        if response.status_code == 200:
            break
        else:
            count += 1
    if count == 3:
        res = f"未查询到{address}天气信息"
    else:
        response = response.json()
        res = response['data']['content']
    return res

def get_user_pressure():
    var = ContextVar('vae')
    print(var.get())



if __name__ == '__main__':
    # print(get_location_weather('杭州'))
    var = ContextVar('vae')
    var.set(123456)
    get_user_pressure()

    

# 假设你的时间戳是以毫秒为单位
timestamp = 1726728699819

# 将时间戳从毫秒转换为秒
