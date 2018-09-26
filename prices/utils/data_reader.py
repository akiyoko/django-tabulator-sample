import logging
import time
from urllib.parse import urlencode

import pandas as pd
import requests
from django.conf import settings
from django.core.cache import cache
from .date_utils import DateOfYear


logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 60 * 60 * 3  # 3 hours


def get_btc_prices(year=2018):
    """Poloniex API を利用して BTC 価格データを取得"""
    start_time = time.time()

    key = 'prices:btc:{}'.format(year)
    # キャッシュからデータを取得する
    data = cache.get(key)

    # キャッシュにデータがなかった場合は API から取得する
    if not data:
        logger.debug("キャッシュに BTC 価格データが見つからなかったので API から取得")
        target_url = '{}?{}'.format(
            'https://poloniex.com/public',
            urlencode(dict(
                command='returnChartData',
                currencyPair='USDT_BTC',
                start=DateOfYear(2018).start_date_unixtime,  # 年初の UNIX 時間
                end=DateOfYear(2018).end_date_unixtime,  # 年末の UNIX 時間
                period=60 * 60 * 24,  # 日足データ
            ))
        )
        df = pd.read_json(target_url)
        df = df.set_index(pd.to_datetime(df['date']))
        # JST に変換
        df.index = df.index + pd.DateOffset(hours=9)
        df['Date'] = pd.to_datetime(df['date'])
        df['Price (USD)'] = df['close']
        df['Symbol'] = 'BTC'

        # dict のリスト形式でキャッシュに保存
        cache.set(key, df.to_dict(orient='record'), CACHE_TIMEOUT)
    else:
        logger.debug("キャッシュに BTC 価格データが見つかった")
        df = pd.DataFrame.from_dict(data)
        df = df.set_index(pd.to_datetime(df['date']))

    logger.debug("get_btc_prices finished in {:.2f} secs.".format(
        time.time() - start_time))
    return df


def get_usd_jpy_prices():
    """Quandl API を利用してドル円の日足データを取得"""
    start_time = time.time()

    key = 'prices:usd-jpy'
    # キャッシュからデータを取得する
    data = cache.get(key)

    # キャッシュにデータがなかった場合は API から取得する
    if not data:
        logger.debug("キャッシュに USD/JPY データが見つからなかったので API から取得")
        target_url = '{}?{}'.format(
            'https://www.quandl.com/api/v3/datasets/FRED/DEXJPUS/data.json',
            urlencode(dict(
                start_date=DateOfYear(2018).start_date_yyyymmdd_dash,  # 2018-01-01
                end_date=DateOfYear(2018).end_date_yyyymmdd_dash,  # 2018-12-31
                order='asc',
                api_key=settings.QUANDL_API_KEY,
            ))
        )
        res_json = requests.get(target_url).json()
        result = res_json['dataset_data']['data']
        df = pd.DataFrame(
            result,
            columns=['Date', 'USD/JPY'],
        )
        df = df.set_index(pd.to_datetime(df['Date']))
        df['Date'] = pd.to_datetime(df['Date'])

        # dict のリスト形式でキャッシュに保存
        cache.set(key, df.to_dict(orient='record'), CACHE_TIMEOUT)
    else:
        logger.debug("キャッシュに USD/JPY データが見つかった")
        df = pd.DataFrame.from_dict(data)
        df = df.set_index(pd.to_datetime(df['Date']))

    logger.debug("get_usd_jpy_prices finished in {:.2f} secs.".format(
        time.time() - start_time))
    return df


def get_prices():
    # BTC価格
    df_btc = get_btc_prices()
    print('df_btc=')
    print(df_btc)
    # USD/JPY
    df_usd_jpy = get_usd_jpy_prices()
    print('df_usd_jpy=')
    print(df_usd_jpy)

    # 'Date' をキーにしてマージ
    df = pd.merge(df_btc, df_usd_jpy, on='Date', how='outer')
    # Forward fill する前にソート
    df['id'] = df.index
    df = df.sort_values(by=['Date', 'id'])
    df = df.reset_index(drop=True)
    # Forward fill で隙間を埋める
    df['USD/JPY'] = df['USD/JPY'].fillna(method='ffill')

    # 円換算
    df['Price (JPY)'] = df['Price (USD)'] * df['USD/JPY']
    # 前日からの上昇率を計算
    df['Price diff'] = df['Price (JPY)'] - df['Price (JPY)'].shift(1)
    df['Price diff rate'] = df['Price diff'] / df['Price (JPY)'].shift(1)

    # 価格が存在しないデータを削除
    df = df.dropna(subset=['Price (USD)'])
    # df = df[df['Date'].dt.year == 2018]
    # NaN を 0 に変換
    df = df.fillna(0)

    return df
