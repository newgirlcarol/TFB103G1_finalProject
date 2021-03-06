from datetime import datetime
import pandas as pd
import json
import os
from conn_mysql import *

# Create a directory to save json for LINE bot FlexSendMessage
def hotRank_mkdir():
    if not os.path.isdir('./line_bot_card'):
        os.makedirs('./line_bot_card')

# Get last 7 days data from today
def get_week_log_data():
    today = datetime.today()
    year = datetime.today().year
    yesterdayData = pd.read_csv(
        f'./data/user_mainRS_log/{year}/mainRS_log_{today.year}-{today.month}-{today.day-1}.csv',
        encoding='utf-8',
        header=None)
    # Append last 6 days data to yesterdayData
    for i in range(2, 8):
        try:
            data = pd.read_csv(f'./data/user_mainRS_log/{year}/mainRS_log_{today.year}-{today.month}-{today.day-i}.csv', encoding='utf-8', header=None)
            yesterdayData = pd.concat([yesterdayData, data], axis=0)
        except FileNotFoundError:
            pass
    return yesterdayData

def get_top5_hotel():
    data = get_week_log_data()
    top5_hotels = data.groupby(1, as_index=False).count().sort_values(by=0, ascending=0).iloc[:5, 0]
    top5 = [hotel for hotel in top5_hotels]  # -> [hotel_1, hotel_2, hotel_3, hotel_4, hotel_5]
    return top5

def get_top5_url(top5):
    host, user, pwd, db = get_mysql_config()
    conn, cursor = conn_mysql(host=host, user=user, pwd=pwd, db=db)
    tmpList = list()
    for hotel in top5:
        sql = f'SELECT bnb_url FROM bnb WHERE bnb_name = "{hotel}";'
        cursor.execute(sql)
        try:
            tmpList.append(cursor.fetchall()[0][0])
        except IndexError:
            # If url is empty, return home page
            tmpList.append('https://www.booking.com/index.zh-tw.html')
    close_conn_mysql(conn, cursor)
    return tmpList

# Insert top5, top5_url into button json
def get_hotRank_button():
    hotRank_mkdir()
    top5 = get_top5_hotel()         # top5 = [hotel_1, hotel_2, hotel_3, hotel_4, hotel_5]
    top5_url = get_top5_url(top5)   # url  = [url_1, url_2, url_3, url_4, url_5]
    button = json.load(open('./line_bot_card/card_hotRank_button.json', 'r', encoding='utf-8'))
    for i in range(0, 5):
        button['footer']['contents'][i]['action']['label'] = top5[i]
        button['footer']['contents'][i]['action']['uri'] = top5_url[i]
    return button

