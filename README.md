# transit_time_comparison_app

iphoneから位置情報を取得することで、ある二地点の移動にかかる時間を記録するためのアプリ

測定開始箇所と測定終了箇所の緯度経度を設定できる。測定開始箇所にiphoneが移動した際に
時間、経路、日を測定開始し測定終了箇所に移動した際にこれを終了する。

記録したdataはDBに保存されるため、参照することができる。

GUIにクロスプラットフォームであるkivyを用いている。

# Features
Mysqlを使用しており、テーブル内には以下のカラムが存在する。
id:int型:計測番号
time:datetime型：計測時間
date:datetime型；計測日
trajectory:json(配列)：移動地点の軌跡
Mysqlでは配列は直接使用できないためjson型を使用することで
間接的に配列を使用している。
# Requirement

![menu](https://user-images.githubusercontent.com/18396212/168289594-b39d4aa5-989b-45b3-abed-41f3d57472fe.jpg)

# Installation

Requirementで列挙したライブラリなどのインストール方法を説明する

```bash
pip install huga_package
```

# Usage

DEMOの実行方法など、"hoge"の基本的な使い方を説明する

```bash
git clone https://github.com/hoge/~
cd examples
python demo.py
```

# Note

注意点などがあれば書く

# Author

作成情報を列挙する

* 作成者
* 所属
* E-mail

# Name（リポジトリ/プロジェクト/OSSなどの名前）
 
分かりやすくてカッコイイ名前をつける（今回は"hoge"という名前をつける）
 
"hoge"が何かを簡潔に紹介する
 
# DEMO
 
"hoge"の魅力が直感的に伝えわるデモ動画や図解を載せる
 
# Features
 
"hoge"のセールスポイントや差別化などを説明する
 
# Requirement
 
"hoge"を動かすのに必要なライブラリなどを列挙する
 
* huga 3.5.2
* hogehuga 1.0.2
 
# Installation
 
Requirementで列挙したライブラリなどのインストール方法を説明する
 
```bash
pip install huga_package
```
 
# Usage
 
DEMOの実行方法など、"hoge"の基本的な使い方を説明する
 
```bash
git clone https://github.com/hoge/~
cd examples
python demo.py
```
 
# Note
 
注意点などがあれば書く
 
# Author
 
作成情報を列挙する
 
* 作成者
* 所属
* E-mail
 
# License
ライセンスを明示する
 
"hoge" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).
 
社内向けなら社外秘であることを明示してる
 
"hoge" is Confidential.
