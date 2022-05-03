from kivy.app import App
from kivy.lang import Builder
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import NoTransition, FadeTransition
import time
import datetime
import threading
from kivy.clock import Clock
import mysql.connector as mydb
import datetime
import json
from pyicloud import PyiCloudService
import sys
import matplotlib.pyplot as plt
import numpy as np
from kivy.uix.stacklayout import StackLayout
# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenMansager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
Builder.load_file('./layout.kv')

from kivy_garden.mapview import MapView, MapMarker
from kivy.app import App

IC_PASS = '********'
IC_USER = '********'
DB_PASS = '********'
DB_USER = '********'

END_TR = [35.681473, 139.757559]
START_TR = [35.681473, 139.757559]
STATE_LOCATION = [35.681473, 139.757559]

R = 50

def get_database():
    # コネクションの作成
    conn = mydb.connect(
        host='localhost',
        port='3306',
        user=DB_USER,
        password=DB_PASS,
        database='test'
    )

    # コネクションが切れた時に再接続してくれるよう設定
    conn.ping(reconnect=True)
    # DB操作用にカーソルを作成
    cur = conn.cursor()
    # テーブルの作成
    cur.execute(
        """
        select * from test_table3
        """
    )
    info = {}
    for (id, time, date, jsonf) in cur:
        info[id] = {'time':time, 'date':date, 'trajectory':json.loads(jsonf)}
        
    conn.commit()
    conn.close()

    return info

class MapViewLayout(MapView):
    def __init__(self, **kwargs):
        super(MapViewLayout, self).__init__(**kwargs)
        self.info = get_database()
        for id in self.info.keys():
            self.add_marker(MapMarker(lat=self.info[id]['trajectory']['latitude'][0], lon=self.info[id]['trajectory']['longitude'][0]))

class AutoMeasureLayout(TabbedPanel):
    now_state  = StringProperty() 
    control = StringProperty()
    measure_time = StringProperty()
    now_measurement = BooleanProperty()
    time = StringProperty()
    def __init__(self, **kwargs):
        super(AutoMeasureLayout, self).__init__(**kwargs)
        self.now_state = 'Measurement betwean two point'
        self.control = 'Start'
        self.first_measurement = True
        self.now_measurement = False
        self.end_tr = END_TR
        self.start_tr = START_TR
        self.state_location = STATE_LOCATION
        self.time = '00:00:00'
        self.id = 0
        self.counter = 0
        self.start_location = True
        self.r = R
        
        self.trajectory = {
            "latitude":[],
            "longitude":[]
            }
        
    def buttonClicked_start(self):        # ボタンをクリック時
        list_tr = eval(self.ids.start_tr.text)
        #これの形式に変更
        self.start_tr = [list_tr[0], list_tr[1]] 
        
    def buttonClicked_end(self):        # ボタンをクリック時
        list_tr = eval(self.ids.end_tr.text)
        self.end_tr = [list_tr[0], list_tr[1]]

    def buttonClicked(self):        # ボタンをクリック時
        #計測中→待機画面中
        if self.now_measurement:
            self.reset_timer()
            self.now_state = 'Measurement betwean two point'
            self.control = 'Start'
            
        #待機画面→計測中
        elif not(self.now_measurement):
            self.start_waiting()
            self.now_state = 'We are taking measurements now'
            self.control = 'Reset'

    def on_count(self, dt):
        td = datetime.timedelta(seconds=time.time() - self.start)
        m, s = divmod(td.seconds, 60)
        h, m = divmod(m, 60)
        self.time = '{0:02}:{1:02}:{2:02}'.format(h, m, s)

        
    def start_timer(self):
        self.start = time.time()
        Clock.schedule_interval(self.on_count, 1.0)
        # Clock.schedule_interval(self.get_location, 10)
        pass
    
    def reset_timer(self):
        self.now_measurement = False
        if self.start_location:
            Clock.unschedule(self.get_location)
        else:
            Clock.unschedule(self.on_count)
            Clock.unschedule(self.get_location)
            self.time = '00:00:00'

            self.trajectory = {
                "latitude":[],
                "longitude":[]
            }
        

    def stop_timer(self):
        self.now_measurement = False
        Clock.unschedule(self.on_count)
        self.time = '00:00:00'
        self.id = self.id + 1
    

            
    def start_waiting(self):
        self.now_measurement = True
        Clock.schedule_interval(self.get_location, 5)
        
    def stop_waiting(self):
        # Clock.unschedule(self.get_location)
        pass

    def start_measurement(self):
        self.start_location = False
        self.start_timer()

    def stop_measuring(self):
        Clock.unschedule(self.get_location)
        self.start_location = True
        self.stop_timer()
        self.store_database()
        self.trajectory = {
                "latitude":[],
                "longitude":[]
        }
        self.now_state = 'Measurement betwean two point'
        self.control = 'Start'

    def get_location(self,dt):
        api = PyiCloudService(IC_USER, IC_PASS)

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

        if self.start_location:
            # 計測開始地点
            a, b = calc_xy(self.start_tr[0] , self.start_tr[1], self.state_location[0] , self.state_location[1])
            x, y = calc_xy(lat, lon, self.state_location[0] , self.state_location[1])

            if np.sqrt((x-a)**2+(y-b)**2) < self.r:
                self.stop_waiting()
                self.start_measurement()
        else:
            # 計測終了地点

            self.trajectory['latitude'].append(lat)
            self.trajectory["longitude"].append(lon)

            a, b = calc_xy(self.end_tr[0] , self.end_tr[1], self.state_location[0] , self.state_location[1])
            x, y = calc_xy(lat, lon, self.state_location[0] , self.state_location[1])

            if np.sqrt((x-a)**2+(y-b)**2) < self.r:
                self.stop_measuring()

    # def get_location_measuring(self,dt):
    #     api = PyiCloudService(IC_USER, IC_PASS)

    #     #ここから2段認証を実施する。
    #     if api.requires_2fa:
    #         import click
    #         print ("Two-factor authentication required. Your trusted devices are:")

    #         devices = api.trusted_devices
    #         for i, device in enumerate(devices):
    #             print ("  %s: %s" % (i, device.get('deviceName',
    #                 "SMS to %s" % device.get('phoneNumber'))))

    #         device = click.prompt('Which device would you like to use?', default=0)
    #         device = devices[device]
    #         if not api.send_verification_code(device):
    #             print ("Failed to send verification code")
    #             sys.exit(1)

    #         code = click.prompt('Please enter validation code')
    #         if not api.validate_verification_code(device, code):
    #             print ("Failed to verify verification code")
    #             sys.exit(1)

    #     auth = str(self.get_oauth(api))
    #     eval_auth = eval(auth)
    #     lat = eval_auth['latitude']
    #     lon = eval_auth['longitude']
    #     self.trajectory['latitude'].append(lat)
    #     self.trajectory["longitude"].append(lon)
        


    def get_oauth(self, api):
        auth = api.devices[2].location()
        return auth

    def store_database(self):
        
        # コネクションの作成
        conn = mydb.connect(
            host='localhost',
            port='3306',
            user=DB_USER,
            password=DB_PASS,
            database='test'
        )

        # コネクションが切れた時に再接続してくれるよう設定
        conn.ping(reconnect=True)
        # DB操作用にカーソルを作成
        cur = conn.cursor()
        # cur.execute('DROP TABLE test_table4')
        # テーブルの作成
        # cur.execute(
        #     """
        #     CREATE TABLE test_table4(
        #     `id` int auto_increment primary key,
        #     `time` char(8) not null,
        #     `date` datetime not null,
        #     `trajectory` json
        #     )
        #     """)
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



class CustomStackLayout(StackLayout):
    def __init__(self, **kwargs):
        super(CustomStackLayout, self).__init__(**kwargs)
        # データベース情報の取得self.info
        self.info = get_database()
        # 取得情報のゲット
        self.display_setting()

    def display_setting(self):

        lab = Button(text=str('id'), width=40, size_hint=(0.1, 0.1), background_color=(1, 1, 1, 1))
        self.add_widget(lab)
        lab = Button(text=str('date'), width=40, size_hint=(0.3, 0.1))
        self.add_widget(lab)
        lab = Button(text=str('time'), width=40, size_hint=(0.3, 0.1))
        self.add_widget(lab)
        lab = Button(text=str('distance'), width=40, size_hint=(0.3, 0.1))#+str(self.info[id]['time'])), width=40, size_hint=(0.3, 0.1))
        self.add_widget(lab)

        for id in self.info.keys():
            lab = Button(text=str(id), width=40, size_hint=(0.1, 0.1))
            self.add_widget(lab)
            lab = Button(text=str(self.info[id]['date']), width=40, size_hint=(0.3, 0.1))
            self.add_widget(lab)
            lab = Button(text=str(self.info[id]['time']), width=40, size_hint=(0.3, 0.1))
            self.add_widget(lab)
            distance = calc_distance(self.info[id]['trajectory']['latitude'],self.info[id]['trajectory']['longitude'])
            lab = Button(text=str(round(distance, 2)), width=40, size_hint=(0.3, 0.1))#+str(self.info[id]['time'])), width=40, size_hint=(0.3, None))
            self.add_widget(lab)

        # date, time, 距離を表示させたい

def calc_distance(latitude, longitude):
    distance = 0
    ## 東京駅付近を基準
    s_lat = 35.681473
    s_lon = 139.757559

    b_x, b_y = calc_xy(latitude[0], longitude[0], s_lat, s_lon)

    for i in range(len(latitude) - 1):
        a_x, a_y = calc_xy(latitude[i+1], longitude[i+1], s_lat, s_lon)
        
        dx = a_x - b_x
        dy = a_y - b_y
        distance = distance + np.sqrt(dx**2 + dy**2)

        b_x = a_x
        b_y = a_y
    
    return distance/1000

def calc_xy(phi_deg, lambda_deg, phi0_deg, lambda0_deg):

#参考https://qiita.com/sw1227/items/e7a590994ad7dcd0e8ab

    """ 緯度経度を平面直角座標に変換する
    - input:
        (phi_deg, lambda_deg): 変換したい緯度・経度[度]（分・秒でなく小数であることに注意）
        (phi0_deg, lambda0_deg): 平面直角座標系原点の緯度・経度[度]（分・秒でなく小数であることに注意）
    - output:
        x: 変換後の平面直角座標[m]
        y: 変換後の平面直角座標[m]
    """
    # 緯度経度・平面直角座標系原点をラジアンに直す
    phi_rad = np.deg2rad(phi_deg)
    lambda_rad = np.deg2rad(lambda_deg)
    phi0_rad = np.deg2rad(phi0_deg)
    lambda0_rad = np.deg2rad(lambda0_deg)

    # 補助関数
    def A_array(n):
        A0 = 1 + (n**2)/4. + (n**4)/64.
        A1 = -     (3./2)*( n - (n**3)/8. - (n**5)/64. ) 
        A2 =     (15./16)*( n**2 - (n**4)/4. )
        A3 = -   (35./48)*( n**3 - (5./16)*(n**5) )
        A4 =   (315./512)*( n**4 )
        A5 = -(693./1280)*( n**5 )
        return np.array([A0, A1, A2, A3, A4, A5])

    def alpha_array(n):
        a0 = np.nan # dummy
        a1 = (1./2)*n - (2./3)*(n**2) + (5./16)*(n**3) + (41./180)*(n**4) - (127./288)*(n**5)
        a2 = (13./48)*(n**2) - (3./5)*(n**3) + (557./1440)*(n**4) + (281./630)*(n**5)
        a3 = (61./240)*(n**3) - (103./140)*(n**4) + (15061./26880)*(n**5)
        a4 = (49561./161280)*(n**4) - (179./168)*(n**5)
        a5 = (34729./80640)*(n**5)
        return np.array([a0, a1, a2, a3, a4, a5])

    # 定数 (a, F: 世界測地系-測地基準系1980（GRS80）楕円体)
    m0 = 0.9999 
    a = 6378137.
    F = 298.257222101

    # (1) n, A_i, alpha_iの計算
    n = 1. / (2*F - 1)
    A_array = A_array(n)
    alpha_array = alpha_array(n)

    # (2), S, Aの計算
    A_ = ( (m0*a)/(1.+n) )*A_array[0] # [m]
    S_ = ( (m0*a)/(1.+n) )*( A_array[0]*phi0_rad + np.dot(A_array[1:], np.sin(2*phi0_rad*np.arange(1,6))) ) # [m]

    # (3) lambda_c, lambda_sの計算
    lambda_c = np.cos(lambda_rad - lambda0_rad)
    lambda_s = np.sin(lambda_rad - lambda0_rad)

    # (4) t, t_の計算
    t = np.sinh( np.arctanh(np.sin(phi_rad)) - ((2*np.sqrt(n)) / (1+n))*np.arctanh(((2*np.sqrt(n)) / (1+n)) * np.sin(phi_rad)) )
    t_ = np.sqrt(1 + t*t)

    # (5) xi', eta'の計算
    xi2  = np.arctan(t / lambda_c) # [rad]
    eta2 = np.arctanh(lambda_s / t_)

    # (6) x, yの計算
    x = A_ * (xi2 + np.sum(np.multiply(alpha_array[1:],
                                    np.multiply(np.sin(2*xi2*np.arange(1,6)),
                                                np.cosh(2*eta2*np.arange(1,6)))))) - S_ # [m]
    y = A_ * (eta2 + np.sum(np.multiply(alpha_array[1:],
                                        np.multiply(np.cos(2*xi2*np.arange(1,6)),
                                                    np.sinh(2*eta2*np.arange(1,6)))))) # [m]
    # return
    return x, y # [m]






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

    #     thread = threading.Thread(target=self.process)
    #     thread.start()

    # def process(self):
        #以下は接続するicloudのアカウントとパスワードを記載します。
        api = PyiCloudService(IC_USER, IC_PASS)

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
            user=DB_USER,
            password=DB_PASS,
            database='test'
        )

        # コネクションが切れた時に再接続してくれるよう設定
        conn.ping(reconnect=True)
        # DB操作用にカーソルを作成
        cur = conn.cursor()
        # cur.execute('DROP TABLE test_table4')
        # テーブルの作成
        # cur.execute(
        #     """
        #     CREATE TABLE test_table4(
        #     `id` int auto_increment primary key,
        #     `time` char(8) not null,
        #     `date` datetime not null,
        #     `trajectory` json
        #     )
        #     """)
        # conn.commit()
        
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
        return AutoMeasureLayout()

    # def update_time(self, nap):
    #     self.measure_time = time.time() - float(self.root.ids.start.text)
    #     test = self.measure_time
    #     self.root.ids.time.text = time.strftime("[b]%H[/b]:%M:%S", time.time())
        
    # def on_start(self):
    #     Clock.schedule_interval(self.update_time, 1)

if __name__ == '__main__':
    TestTabPanelApp().run()