from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import requests
import json

webhookUrl = "https://discord.com/api/webhooks/1114774385543368795/l4P-nYmqwqmcO_AJWtPNwK3X_5kvHISKKw5jtMjvfblwsceUivtcrLlDb7owVW4-hnIA"
address = ('0.0.0.0', 8000)

class MyHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        parsed_path = urlparse(self.path)
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'Hello from do_GET')

    def do_POST(self):

        parsed_path = urlparse(self.path)
        content_length = int(self.headers['content-length'])

        sentDiscord.readJson('{}'.format((self.rfile.read(content_length).decode('utf-8'))))

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'Hello from do_POST')


class sentDiscord():

    '''
    Discord Webhookにメッセージ送信する
    '''
    def sendDiscord(self, msg):

        # Create JSON
        payload = {
        "content" : "{0}".format(msg)
        }

        # Send to Discord
        res = requests.post(webhookUrl, json.dumps(payload), headers={'Content-Type': 'application/json'})
        return


    '''
    Webサーバから受け取ったJSONを辞書に変換してメッセージを作成する
    '''
    def readJson(self, jsonData):
        jsonData = json.loads(jsonData)

        '''
        緊急地震速報かつ第一報かつ予想震度3以上なら処理させる
        '''

        # get first eew message
        if jsonData.get('type') == 'eew' and jsonData.get('report') == '1' and int(jsonData.get('intensity')) > 2:
            magnitude = float(jsonData.get('magnitude'))

            # get EQ Data
            epicenter = str(jsonData.get('epicenter'))
            depth = str(jsonData.get('depth'))
            intensity = str(jsonData.get('intensity'))

            '''
            discordの出力メッセージ作成部分。fixを指定すると全文黄色にできる。
            '''
            # add EQ Data
            msg = '''```fix

    地　震　速　報　（第１報）

    震　　源　　：　　{0}
    予想震度　　：　　{1}
    規　　模　　：　　M{2}
    深　　さ　　：　　{3}

    ```'''.format(epicenter, intensity, str(magnitude), depth)
            self.sendDiscord(msg)    
            return

        '''
        誤報の場合はpga_alert_cancelが送られてくる「らしい」のでそちらも検知するようにする
        '''
        # Alert Cancel
        if jsonData.get('type') == 'pga_alert_cancel':
            msg = '### Cancel Message ###'
            self.sendDiscord(msg)
            return

def run():
    server = HTTPServer(address, MyHTTPRequestHandler)
    server.serve_forever()