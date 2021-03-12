# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 07:11:40 2020

@author: Novin
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 07:02:19 2020

@author: Novin
"""

import pandas as pd
from datetime import datetime
from dateutil.parser import parse


# pair for selected currency pair such as EURUSD
# options for all keywords related to currency pair as string list
# df for dataframe of total news
def exportNews(pair, options, df):
    subDF = []
    df_date = []
    df_time = []
    for i, row in df.iterrows():

        if list(filter(lambda x: x in str(row['keywords']), options)):
            subDF.append(row)
            dt = parse(row['pubDate'])
            df_date.append(dt.date())
            df_time.append(dt.time())

    subdf = pd.DataFrame(subDF)
    subdf['date'] = df_date
    subdf['time'] = df_time
    subdf.to_excel(str(pair) + 'news.xlsx')
    return subdf