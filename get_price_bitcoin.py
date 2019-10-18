# -*- coding: utf-8 -*-

# インポート
import requests
import time
from datetime import datetime
from influxdb import InfluxDBClient

# Url取得
Url = 'https://api.coinmarketcap.com/v1/ticker/'


# メインメソッド
def main():
    # 永遠価格を取得するため、繰り返しWhileを使う
    while True:
        # 現在時刻を取得。DBへ登録する時に使う
        now = datetime.now()
        time_now = now.strftime("%Y-%m-%d %H:%M")

        # bitcoinに関する情報をリクエストを投げて、返ってくる結果はresponseに代入する
        response = requests.get(Url + 'bitcoin')

        # responseに入っている値をjson型に変換する
        response_json = response.json()

        # jsonに変換したresponseの中にprice_usdの値をfloat型に変換して価格（price）に代入する
        price = float(response_json[0]['price_usd'])

        # 時間と価格を出力
        # print(time_now,' Bitcoin price = ',price)

        # InfluxDBに接続するために必要な情報を保持する
        client = InfluxDBClient('localhost', 8086)
        # DBに登録する情報を作成する
        body = [{
            'measurement': 'bitcoin_price',
            # 'time': time_now,
            'fields': {
                'price': price
            }
        }]
        # InfluxDBにデータを書き込む
        client.write_points(body, database='bitcoin_price', time_precision='n')

        # １分毎に価格を取得設定
        time.sleep(60)


# メイン処理
if __name__ == '__main__':
    main()
