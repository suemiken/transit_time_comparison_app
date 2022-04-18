import mysql.connector as mydb
import datetime
import json

# コネクションの作成
conn = mydb.connect(
    host='localhost',
    port='3306',
    user='*******',
    password='**********',
    database='test'
)

# コネクションが切れた時に再接続してくれるよう設定
conn.ping(reconnect=True)

# 接続できているかどうか確認
print(conn.is_connected())

# DB操作用にカーソルを作成
cur = conn.cursor()

#　テーブルの削除
cur.execute('DROP TABLE test_table')

# テーブルの作成
cur.execute(
    """
    CREATE TABLE test_table(
    `id` int auto_increment primary key,
    `time` datetime not null,
    `date` datetime not null,
    `trajectory` json
    )
    """)
conn.commit()

date1 = datetime.datetime.now()
date2 = datetime.datetime.now()
trajectry = {
    "latitude":[0.1,0.2],
    "longitude":[1,2]
    }

json_trajectry = json.dumps(trajectry)

cur.execute(
    """
    INSERT INTO test_table VALUES (
        9, 
        %s,
        %s,
        %s
    )
    """, (date1, date2, json_trajectry))

conn.commit()
conn.close()