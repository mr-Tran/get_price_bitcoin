# -*- coding: utf-8 -*-

# インポート
import time
import os
import requests
import urllib.parse

from email.mime.text import MIMEText
from smtplib import SMTP_SSL as SMTP
from influxdb import InfluxDBClient


# 定数定義

host = "localhost"  # ホスト
port = 8086  # ポート番号
sleep_time = 60  # 値段を再取得間隔（秒）
best_bid_hope = 500000  # 最低売値希望
best_ask_hope = 1000000  # 最高売値希望

# メール送信用
SMTP_Host = 'smtp.gmail.com'  # SMTP(メール送信用) ホスト
sender = 'gyomutestsample@gmail.com'  # 送信側のメールアドレス
password = "Testtest123456"  # パスワード
receivers = ['gyomutestsample@gmail.com']  # 受信側メールアドレス
username = "Mr.Sample"  # ユーザー名
bitflyer_site_url = "https://bitflyer.com/ja-jp/"  # bitFlyerサイトのurl\
text_subtype = 'plain'  # テキストタイプ
subject = "【緊急】ビットコイン値段は希望金額範囲以外"  # 件名
# メールコンテンツ（メール内容）
content = username + """　様

いつもbitFlyerをご利用いただき、誠にありがとうございます。

ビットコインの値段は希望金額範囲以外でした。
早急に購入・売却手続きをお願いいたします。
ログインはこちらから:　""" + bitflyer_site_url + """

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

# Slack送信用
token = "xoxp-811027316566-810675147927-811055670742-aefa70265b368effccffa5c4aa5d7729" # slackのtoken
slack_username = "Slack support" # Slackで送信者名
slack_url = "https://slack.com/api/chat.postMessage" # Slack API(メッセージを送信する用)
slack_channel = "test" # Slackのチャンネル名
# Slackで送信するメッセージ内容
slack_content = username + "様\n\nいつもbitFlyerをご利用いただき、誠にありがとうございます。\n\nビットコインの値段は希望金額範囲以外でした。\n早急に購入・売却手続きをお願いいたします。\nログインはこちらから:　" + bitflyer_site_url + "\n今後ともbitFlyerをよろしくお願い致します。\n\n※ 本メールは送信専用です。返信はお受けしておりませんのでご了承ください。\n※ 本メールにお心当たりのない場合や、ご意見・ご質問等がございましたら下部のお問い合わせ先よりお知らせください。\n\n--------------------------------------------------\n株式会社 sample\n〒123-4567　東京都新宿区東新宿 1-2-3 ミサンプルタワー\n仮想通貨交換業者（登録番号 関東財務局長 第 1X2Y3Z 号）\nお問い合わせ電話番号： 03-1234-5678（受付時間 10:00〜19:00）\n--------------------------------------------------"



# メールを送信するメソッド
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

        # 送信側のメールアドレスでログインする
        conn.login(sender, password)
        try:
            # 正常の場合はメールを送信する
            conn.sendmail(sender, receivers, msg.as_string())

        finally:
            # 終了時に常に行う処理
            conn.quit()
    except Exception as e:
        # エラーが発生する時にエラー内容を出力する
        print(e)


# Slackに通知するメソッド
# def sendSlack():
#     try:
#         # Slackで通知する際に必要なデータを設定する
#         data = {
#             'token': token,
#             'channel': channel,
#             'text': content,
#             'username': username_slack
#         }
#
#         # POSTメソッドで送信する
#         response = requests.post(slack_url, data=data)
#
#     except Exception as e:
#         print(e)

# curlコマンドを実行するメソッド
def executeCurlCommand():
    try:
        # Slackに送信するメッセージ内容をエンコードする。
        slack_content_quote = urllib.parse.quote(slack_content)

        # 実行するコマンドを生成する
        curl_cmd = 'curl -XPOST -d "token='+ token + '" -d "channel=' + slack_channel + '" -d "text=' + slack_content_quote + '" -d "username=' + slack_username + '" "' + slack_url + '"'

        # 実行する
        os.system(curl_cmd)

    except Exception as e:
        print(e)


# メール・Slackを通知判定・送信実施のメソッド
def judgmentSend(notice_status, price):
    try:
        # bitflyerのビットコイン値段でメール通知の判定・送信処理
        # 希望金額が最低希望値以下の場合はステータスの値が「1」にして、メール・Slackを送信する
        if price[0] <= best_bid_hope:
            if notice_status != 1:
                notice_status = 1
                # メール送信メソッドを呼び出す
                sendmail()
                # pythonでslackを通知する
                # sendSlack()
                # curlコマンドを実行、Slackに通知するメソッドを呼び出す
                executeCurlCommand()
        # 希望金額が最大希望値以上の場合はステータスの値が「2」ににして、メール・Slackを送信する
        elif price[1] >= best_ask_hope:
            if notice_status != 2:
                notice_status = 2
                # メール送信メソッドを呼び出す
                sendmail()
                # pythonでslackを通知する
                # sendSlack()
                # curlコマンドを実行、Slackに通知するメソッドを呼び出す
                executeCurlCommand()
        # 上記以外の場合はメールをステータスの値が「0」のまま、メール・Slackを送信しない
        else:
            notice_status = 0
        return notice_status
    except Exception as e:
        print(e)


# 各取引所のビットコイン値段を取得するメソッド
def getPrice():
    # 定数定義
    # APIのurl
    api_url = {'bitFlyer': 'https://api.bitflyer.jp/v1/getboard?product_code=BTC_JPY',
               'Quoine': 'https://api.quoine.com/products/5/price_levels',
               'Zaif': 'https://api.zaif.jp/api/1/depth/btc_jpy',
               'Coincheck': 'https://coincheck.com/api/order_books'}
    try:
        # 各取引所からjson形式でビットコイン値段に関するデータを取得
        bf = requests.get(api_url['bitFlyer']).json()
        qo = requests.get(api_url['Quoine']).json()
        zf = requests.get(api_url['Zaif']).json()
        cc = requests.get(api_url['Coincheck']).json()

        # 取得したデータから購入・売却金額をそれぞれ設定する
        bf_best_bid = bf['bids'][0]['price']  # bitflyerの現在売却金額
        bf_best_ask = bf['asks'][0]['price']  # bitflyerの現在購入金額
        qo_best_bid = qo['buy_price_levels'][0][0]  # Quoineの現在売却金額
        qo_best_ask = qo['sell_price_levels'][0][0]  # Quoineの現在購入金額
        zf_best_bid = zf['bids'][0][0]  # Zaifの現在売却金額
        zf_best_ask = zf['asks'][0][0]  # Zaifの現在購入金額
        cc_best_bid = cc['bids'][0][0]  # Coincheckの現在売却金額
        cc_best_ask = cc['asks'][0][0]  # Coincheckの現在購入金額

        # 設定したデータをリストに詰める
        price_result_list = [bf_best_bid, bf_best_ask, qo_best_bid, qo_best_ask, zf_best_bid, zf_best_ask, cc_best_bid,
                             cc_best_ask]
        return price_result_list
    except Exception as e:
        print(e)


# データベースにデータを登録するメソッド
def insertData(price):
    try:
        # InfluxDBに接続するために必要な情報を保持する
        client = InfluxDBClient(host, port)

        # 表示するため、金額を小数点以下を捨てて丸めする(整数のみにする)
        bf_best_bid = round(float(price[0]), 0)  # bitflyerの現在売却金額
        bf_best_ask = round(float(price[1]), 0)  # bitflyerの現在購入金額
        qo_best_bid = round(float(price[2]), 0)  # Quoineの現在売却金額
        qo_best_ask = round(float(price[3]), 0)  # Quoineの現在購入金額
        zf_best_bid = round(float(price[4]), 0)  # Zaifの現在売却金額
        zf_best_ask = round(float(price[5]), 0)  # Zaifの現在購入金額
        cc_best_bid = round(float(price[6]), 0)  # Coincheckの現在売却金額
        cc_best_ask = round(float(price[7]), 0)  # Coincheckの現在購入金額

        # DBに登録する情報を作成する
        body = [{
            'measurement': 'bitcoin_price',
            'fields': {
                'bf_best_bid': price[0],
                'bf_best_ask': price[1],
                'qo_best_bid': qo_best_bid,
                'qo_best_ask': qo_best_ask,
                'zf_best_bid': price[4],
                'zf_best_ask': price[5],
                'cc_best_bid': cc_best_bid,
                'cc_best_ask': cc_best_ask
            }
        }]
        # InfluxDBにデータを書き込む要求を投げる
        client.write_points(body, database='bitcoin_price_db')

    except Exception as e:
        print(e)


# メインメソッド
def main():
    try:
        # メール通知ステータスを初期化する。送信しない設定。
        before_passing_status = 0

        # 永遠に価格を取得するため、繰り返しWhileを使う
        while True:
            # ビットコイン値段を取得メソッドを呼び出す
            price = getPrice()

            # getPrice()で取得したデータをデータベースに登録する
            insertData(price)

            # メールの通知判定・送信実施のメソッドを呼び出す
            # 通知のステータスをresult_statusに代入する
            result_status = judgmentSend(before_passing_status, price)
            # 変更がある時に通知のステータスがresult_statusの値を設定する。
            # 毎回、ビットコイン値段を取得する度に範囲以外の金額であれば、通知するを防ぐ、希望金額範囲以外の初回のみメールを送信する。
            before_passing_status = result_status

            # 価格を取得間隔設定
            time.sleep(sleep_time)

    except Exception as error:
        # エラーが発生する時にエラー内容を出力する
        print(error)


# メイン処理
if __name__ == '__main__':
    main()
