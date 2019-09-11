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


def get_btc_prices(year=2019):
    """Poloniex API を利用して BTC 価格データを取得"""
    start_time = time.time()

    key = 'prices:btc-usd:{}'.format(year)
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
                start=DateOfYear(year).start_date_unixtime,  # 例：1546268400
                end=DateOfYear(year).end_date_unixtime,      # 例：1577718000
                period=60 * 60 * 24,  # 日足データ
            ))
        )
        df = pd.read_json(target_url)
        # Timestamp 型に変換してタイムゾーンを JST に変更
        df['Date'] = pd.to_datetime(df['date']).dt.tz_localize('Asia/Tokyo')
        # 終値を取得
        df['Price (USD)'] = df['close']
        df['Symbol'] = 'BTC'
        # 列を絞り込む
        df = df[['Date', 'Price (USD)', 'Symbol']]

        # dict のリスト形式でキャッシュに保存
        cache.set(key, df.to_dict(orient='record'), CACHE_TIMEOUT)
    else:
        logger.debug("キャッシュに BTC 価格データが見つかった")
        df = pd.DataFrame.from_dict(data)

    logger.debug("get_btc_prices finished in {:.2f} secs.".format(
        time.time() - start_time))
    return df


def get_usd_jpy_prices(year):
    """Quandl API を利用してドル円の日足データを取得"""
    start_time = time.time()

    key = 'prices:usd-jpy:{}'.format(year)
    # キャッシュからデータを取得する
    data = cache.get(key)

    # キャッシュにデータがなかった場合は API から取得する
    if not data:
        logger.debug("キャッシュに USD/JPY データが見つからなかったので API から取得")
        target_url = '{}?{}'.format(
            'https://www.quandl.com/api/v3/datasets/FRED/DEXJPUS/data.json',
            urlencode(dict(
                start_date=DateOfYear(year).start_date_yyyymmdd_dash, # 2019-01-01
                end_date=DateOfYear(year).end_date_yyyymmdd_dash,     # 2019-12-31
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
        # Timestamp 型に変換してタイムゾーンを JST に変更
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize('Asia/Tokyo')

        # dict のリスト形式でキャッシュに保存
        cache.set(key, df.to_dict(orient='record'), CACHE_TIMEOUT)
    else:
        logger.debug("キャッシュに USD/JPY データが見つかった")
        df = pd.DataFrame.from_dict(data)

    logger.debug("get_usd_jpy_prices finished in {:.2f} secs.".format(
        time.time() - start_time))
    return df


def get_prices(year):
    # BTC価格（ドル）
    df_btc_usd = get_btc_prices(year)
    # print('df_btc=\n{}'.format(df_btc_usd))
    # ドル円
    df_usd_jpy = get_usd_jpy_prices(year)
    # print('df_usd_jpy=\n{}'.format(df_usd_jpy))

    # 'Date' をキーにしてマージ
    df = df_btc_usd.merge(df_usd_jpy, on='Date', how='outer')
    # 日時でソート
    df = df.sort_values('Date')
    # マージによって生じた欠損値を穴埋め（為替市場の取引休業日を考慮）
    df['USD/JPY'] = df['USD/JPY'].ffill().bfill()
    # BTC価格が存在しない行を削除
    df = df.dropna(subset=['Price (USD)'])
    # 円換算
    df['Price (JPY)'] = df['Price (USD)'] * df['USD/JPY']
    # 前日からの上昇率を計算
    df['Price diff'] = df['Price (JPY)'] - df['Price (JPY)'].shift(1)
    df['Price diff rate'] = df['Price diff'] / df['Price (JPY)'].shift(1)

    # Timestamp 型は JSON シリアライズできないので文字列に変換
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S%z')
    # 列を絞り込む
    df = df[['Date', 'Symbol', 'Price (USD)', 'USD/JPY', 'Price (JPY)',
             'Price diff rate']]
    # （初日の上昇率などが NaN になるため）欠損値 を 0 に変換
    df = df.fillna(0)

    return df
