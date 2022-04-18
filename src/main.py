from kivy.app import App
from kivy.lang import Builder
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import NoTransition, FadeTransition
import time
import datetime
from kivy.clock import Clock
import mysql.connector as mydb
import datetime
import json
from pyicloud import PyiCloudService
import sys
# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenMansager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
Builder.load_file('./layout.kv')



class RootWidget(TabbedPanel):
    now_state  = StringProperty() 
    control = StringProperty()
    measure_time = StringProperty()
    now_measurement = BooleanProperty()
    time = StringProperty()
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.now_state = 'Measurement betwean two point'
        self.control = 'Start'
        self.first_measurement = True
        self.now_measurement = False
        self.time = '00:00:00'
        self.id = 0
        self.trajectory = {
            "latitude":[],
            "longitude":[]
            }
        
    def buttonClicked(self):        # ボタンをクリック時
        #計測中→待機画面中
        if self.now_measurement:
            self.stop_timer()
            self.now_state = 'Measurement betwean two point'
            self.control = 'Start'
            
        #待機画面→計測中
        elif not(self.now_measurement):
            self.now_state = 'Two-step verification Waiting'
            self.start_timer()
            self.now_state = 'We are taking measurements now'
            self.control = 'Stop'
        
    
    def on_count(self, dt):
        td = datetime.timedelta(seconds=time.time() - self.start)
        m, s = divmod(td.seconds, 60)
        h, m = divmod(m, 60)
        self.time = '{0:02}:{1:02}:{2:02}'.format(h, m, s)

        
    def start_timer(self):
        self.now_measurement = True
        self.start = time.time()
        Clock.schedule_interval(self.on_count, 1.0)
        Clock.schedule_interval(self.get_location_now, 10)
        pass
    
    def stop_timer(self):
        self.now_measurement = False
        self.store_database()
        Clock.unschedule(self.on_count)
        Clock.unschedule(self.get_location_now)
        self.time = '00:00:00'
        self.id = self.id + 1

    def get_location_now(self,dt):
        #以下は接続するicloudのアカウントとパスワードを記載します。
        api = PyiCloudService('*******', '*******')

        #ここから2段認証を実施する。
        if api.requires_2fa:
            import click
            print ("Two-factor authentication required. Your trusted devices are:")

            devices = api.trusted_devices
            for i, device in enumerate(devices):
                print ("  %s: %s" % (i, device.get('deviceName',
                    "SMS to %s" % device.get('phoneNumber'))))

            device = click.prompt('Which device would you like to use?', default=0)
            device = devices[device]
            if not api.send_verification_code(device):
                print ("Failed to send verification code")
                sys.exit(1)

            code = click.prompt('Please enter validation code')
            if not api.validate_verification_code(device, code):
                print ("Failed to verify verification code")
                sys.exit(1)


        
        auth = str(self.get_oauth(api))
        eval_auth = eval(auth)
        lat = eval_auth['latitude']
        lon = eval_auth['longitude']
        self.trajectory['latitude'].append(lat)
        self.trajectory["longitude"].append(lon)

    def get_oauth(self, api):
        auth = api.devices[2].location()
        return auth

    def store_database(self):
        
        # コネクションの作成
        conn = mydb.connect(
            host='localhost',
            port='3306',
            user='*******',
            password='********',
            database='test'
        )

        # コネクションが切れた時に再接続してくれるよう設定
        conn.ping(reconnect=True)
        # DB操作用にカーソルを作成
        cur = conn.cursor()
        # cur.execute('DROP TABLE test_table4')
        # テーブルの作成
        cur.execute(
            """
            CREATE TABLE test_table4(
            `id` int auto_increment primary key,
            `time` char(8) not null,
            `date` datetime not null,
            `trajectory` json
            )
            """)
        conn.commit()
        
        json_trajectry = json.dumps(self.trajectory)
        self.on_count
        cur.execute(
            """
            INSERT INTO test_table4 VALUES (
                %s, 
                %s,
                %s,
                %s
            )
            """, (self.id, self.time, datetime.datetime.now(), json_trajectry))

        conn.commit()
        conn.close()



class TestTabPanelApp(App):
    def build(self):
        return RootWidget()

    # def update_time(self, nap):
    #     self.measure_time = time.time() - float(self.root.ids.start.text)
    #     test = self.measure_time
    #     self.root.ids.time.text = time.strftime("[b]%H[/b]:%M:%S", time.time())
        
    # def on_start(self):
    #     Clock.schedule_interval(self.update_time, 1)

if __name__ == '__main__':
    TestTabPanelApp().run()