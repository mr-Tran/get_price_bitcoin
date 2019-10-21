# -*- coding: utf-8 -*-

import sys
import time
from datetime import datetime
from email.mime.text import MIMEText
from smtplib import SMTP_SSL as SMTP
from tkinter import messagebox

# インポート
import requests
from influxdb import InfluxDBClient
from selenium import webdriver

# 定数定義
Url = 'https://api.bitflyer.com/v1/ticker/'  # bitFlyerサイト（トップページ）のAPIのUrl
host = "localhost"  # ホスト
port = 8086  # ポート番号
sleep_time = 1  # 値段を再取得間隔（秒）
best_bid_hope = 700000  # 最低売値希望
best_ask_hope = 1000000  # 最高売値希望

SMTP_Host = 'smtp.gmail.com'  # SMTP(メール送信用) ホスト
sender = 'gyomutestsample@gmail.com'  # 送信側のメールアドレス
password = "Testtest123456"  # パスワード
# receivers = ['gyomutestsample@gmail.com']  # 受信側メールアドレス
receivers = ['mengcaicai0520@gmail.com']
username = "Mr.Sample"  # ユーザー名
url = "https://bitflyer.com/ja-jp/"  # bitFlyerサイトのurl\
text_subtype = 'plain'  # テキストタイプ
subject = "【緊急】ビットコイン値段は希望金額範囲以外"  # 件名
# コンテンツ（メール内容）
#content1 = open('content1.txt').read() # 最低で購入希望より下時のお知らせメール内容
#content2 = open('content2.txt').read() # 最大で販売希望より下時のお知らせメール内容
content = username + """　様

いつもbitFlyerをご利用いただき、誠にありがとうございます。

ビットコインの値段は希望金額範囲以外でした。
早急に購入・売却手続きをお願いいたします。
ログインはこちらから:　""" + url + """

今後ともbitFlyerをよろしくお願い致します。

※ 本メールは送信専用です。返信はお受けしておりませんのでご了承ください。
※ 本メールにお心当たりのない場合や、ご意見・ご質問等がございましたら下部のお問い合わせ先よりお知らせください。

--------------------------------------------------
株式会社 sample
〒123-4567　東京都新宿区東新宿 1-2-3 ミサンプルタワー
仮想通貨交換業者（登録番号 関東財務局長 第 1X2Y3Z 号）
お問い合わせ電話番号： 03-1234-5678（受付時間 10:00〜19:00）
--------------------------------------------------

"""
# 最大で販売希望より下時にメールを送信するメソッド
def sendmail():
    try:
        # メッセージを作成する
        msg = MIMEText(content, text_subtype)
        # 件名を設定
        msg['Subject'] = subject
        # 送信元を設定
        msg['From'] = sender
        # SMTPに接続
        conn = SMTP(SMTP_Host)
        # conn.set_debuglevel(False)
        # 送信側のメールアドレスでログインする
        conn.login(sender, password)
        try:
            # 正常の場合はメールを送信する
            conn.sendmail(sender, receivers, msg.as_string())
            print("メールを正常に送信できました。")
        finally:
            # 終了時に常に行う処理
            conn.quit()
    except Exception as error:
        # エラーが発生する時にエラー内容を出力する
        print(error)


# メインメソッド
def main():
    try:
        # 永遠に価格を取得するため、繰り返しWhileを使う
        # driver = webdriver.Chrome()
        # ブラウザを最大化
        # driver.maximize_window()
        # 該当サイトにアクセス
        # driver.get("https://bitflyer.com/ja-jp/")
        notice_flg = 0
        while True:
            # レスポンスを取得
            r = requests.get(Url)
            # jsonに変換
            r_json = r.json()

            # 現在の売り価格 と　現在の買い価格の値を取得
            # 現在の売り価格
            best_bid = float(r_json['best_bid'])
            # 現在の買い価格
            best_ask = float(r_json['best_ask'])

            # DBに書き込む前に確認
            print(' 最低売り価格 = ',best_bid)
            # print(' 最高買い価格 = ', best_ask)

            # InfluxDBに接続するために必要な情報を保持する
            client = InfluxDBClient(host, port)
            # DBに登録する情報を作成する
            body = [{
                'measurement': 'bitcoin_price',
                'fields': {
                    'best_bid': best_bid,
                    'best_ask': best_ask
                }
            }]
            # InfluxDBにデータを書き込む要求を投げる
            client.write_points(body, database='test')
            # メール送信のテストするため、100万以上の値段を設定する
            best_ask = 1000000 
            # 希望金額が最低希望値以下はメールを送信する
            if best_bid <= best_bid_hope:
              if notice_flg == 0:
                sendmail()
                # print("メールを正常に送信できました。")
                notice_flg = 1
            # 希望金額が最大希望値以上はメールを送信する
            elif best_ask >= best_ask_hope:
              if notice_flg == 0:
                sendmail()
                # print("メールを正常に送信できました。")
                notice_flg = 2
            # 上記以外の場合はメールを送信しない
            else:
              notice_flg = 0

            # 価格を取得間隔設定
            time.sleep(sleep_time)
            # driver.refresh()

        # 繰り返し処理が止まっていたら、ブラウザを閉じる
        driver.close()
    except Exception as error:
        # エラーが発生する時にエラー内容を出力する
        print(error)


# メイン処理
if __name__ == '__main__':
    main()
