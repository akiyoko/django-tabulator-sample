import json

import pandas as pd

# pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def test():
    df = pd.DataFrame([
        ['2018-01-01', 1, 2, 3],
        ['2018-01-02', 4, 5, 6],
        ['2018-01-03', 7, 8, 9],
        ['2018-01-05', 10, 11, 12],
    ],
        columns=['x', 'a', 'b', 'c'])
    df2 = pd.DataFrame([
        ['2018-01-02', 90, 91],
        ['2018-01-03 01:00:00', 92, 93],
        ['2018-01-04', 94, 95]
    ], columns=['x', 'd', 'e'])

    # 「Date」をマージ用の共通項目とする（Timestamp 型に変換）
    # 時差がある場合はずらす
    df['Date'] = pd.to_datetime(df['x']) + pd.DateOffset(hours=9)
    df2['Date'] = pd.to_datetime(df2['x'])

    print("df=")
    print(df)
    print(df.to_dict())
    print("df2=")
    print(df2)
    print(df2.to_dict())

    df_merged = df.merge(df2, on='Date', how='outer')
    print("マージ後=")
    print(df_merged)
    df_merged = df_merged.sort_values('Date')
    print("ソート後=")
    print(df_merged)
    # 時系列でソート後に欠損値を穴埋め
    df_merged['e'] = df_merged['e'].ffill().bfill()
    print("欠損値穴埋め後=")
    print(df_merged)
    # オリジナルのものだけ残す
    df_merged = df_merged.dropna(subset=['a'])
    print("スライス後=")
    print(df_merged)
    # 掛け算
    df_merged['f'] = df_merged['a'] * df_merged['e']
    print("掛け算後=")
    print(df_merged)

    # JSON シリアライズ対応
    # Timestamp 型のままだと json.dumps() したとｋに
    # 「TypeError: Object of type 'Timestamp' is not JSON serializable」になるので、文字列に変換
    # https://stackoverflow.com/questions/50404559/python-error-typeerror-object-of-type-timestamp-is-not-json-serializable
    # df['Date'] = df['Date'].astype(str) # -> "Date": "2018-01-01"
    df_merged['Date'] = df_merged['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')  # ->"Date": "2018-01-01 00:00:00"
    print("JSON シリアライズ対応後=")
    print(df_merged)

    # 出力する項目を絞る
    df_merged = df_merged[['Date', 'a', 'b', 'c', 'd', 'e', 'f']]
    print("項目を絞った後=")
    print(df_merged)

    # 念のため欠損値をゼロ埋め
    df_merged = df_merged.fillna(0)
    print("欠損値ゼロ埋め後=")
    print(df_merged)

    print("JSONシリアライズ後=")
    print(json.dumps(df_merged.to_dict(orient='record')))

    pass


def main():
    test()


if __name__ == "__main__":
    main()
