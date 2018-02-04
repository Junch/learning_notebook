
# coding: utf-8

import pandas as pd
import requests
from multiprocessing.dummy import Pool as ThreadPool

lrb_base_url = 'http://api.xueqiu.com/stock/f10/finmainindex.json?page=1&size=10000&symbol='

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Cookie': 'xq_a_token=6bd905936e1ca3ac41374916b0958370575aa86d'
}

def download_lrb(url):
    r = requests.get(url, headers=headers)
    filename = url.split('=')[-1] + '.json'
    print(filename)
    with open(filename, 'wb') as f:
        f.write(r.content)

with open('symbol.txt', 'r', encoding='utf-8') as f:
    symbol = [s.strip() for s in f.readlines()]

lrb_urls = [lrb_base_url + i for i in symbol]

pool = ThreadPool(10)
pool.map(download_lrb, lrb_urls)
pool.close()
pool.join()
