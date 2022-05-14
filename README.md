# transit_time_comparison_app

iphoneから位置情報を取得することで、ある二地点の移動にかかる時間を記録するためのアプリである。
使
測定開始箇所と測定終了箇所の緯度経度を設定できる。測定開始箇所にiphoneが移動した際に
時間、経路、日を測定開始し測定終了箇所に移動した際にこれを終了する。

記録したdataはDBに保存されるため、参照することができる。

GUI:kivy
DB:mysql

Mysqlを使用しており、テーブル内には以下のカラムが存在する。
id:int型:計測番号
time:datetime型：計測時間
date:datetime型；計測日
trajectory:json(配列)：移動地点の軌跡
Mysqlでは配列は直接使用できないためjson型を使用することで
間接的に配列を使用している。

# Requirement and Installation

OS:windows
以下のコマンドを実行することで環境を作成可能
conda env create -f requirement.yml

# Usage
使用するにはicloudのiphoneを捜す機能をＯＮにする必要がある。
また、main.py内の以下の項目を設定する必要がある。

mysqlのユーザ名
mysqlのパスワード
mysqlのデータベース名
mysqlのテーブル名
icloudのアカウント名
icloudのパスワード

すなわち、別途mysqlでテーブルを作成する必要がある。(main.py内にもテーブルを作成するSQL文はあるがDB自体は作成できない)
以下メニュー画面である。STARTボタンを設定することで、スマホへアクセス権の許可を求める通知が来る。
スマホが計測開始地点に移動するとタイマーが動き出し、計測終了地点へ移動するとタイマーが停止し、経路情報と計測時間等がDBへ保存される。

![menu](https://user-images.githubusercontent.com/18396212/168289594-b39d4aa5-989b-45b3-abed-41f3d57472fe.jpg)

しかし、デフォルトの計測開始、終了地点の緯度経度は東京駅付近となっており、settingで設定する必要がある。
以下の画面で入力することで設定可能である。

![setting](https://user-images.githubusercontent.com/18396212/168415326-8b53f2c2-c4a6-4a02-a1ba-45453e4c2d50.jpg)

記録した物は以下の画面で確認できる。

![recoding List](https://user-images.githubusercontent.com/18396212/168415321-3a30faba-d092-46dc-ae69-a08b38a13245.jpg)

mapviewの画面は将来的に指定したidの測定情報を地図上で表示できるようにしたい。

測定した経路はconf_locaten.pyで描画することによって、視覚的にどのような経路をたどったか確認できる。ただし、道路情報はなく、背景は白紙である。

