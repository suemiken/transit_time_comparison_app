import mysql.connector as mydb
import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import pickle

 # コネクションの作成
conn = mydb.connect(
    host='localhost',
    port='3306',
    user='****',
    password='***',
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

for (id, time, date, jsonf) in cur:
    trajectory=jsonf

trajectory = json.loads(trajectory)

lat = trajectory['latitude']
lon = trajectory['longitude']
print(len(lat))
plt.scatter(lat, lon)
plt.show()

f = open('lat.binaryfile', 'wb')
pickle.dump(lat, f)
f.close
f = open('lon.binaryfile', 'wb')
pickle.dump(lon, f)
f.close
# print(cur)
            # `id` int auto_increment primary key,
            # `time` char(8) not null,
            # `date` datetime not null,
            # `trajectory` json
conn.commit()
conn.close()