# Convert data v3

MongoDB内の`nr_setting`、`ar_setting`を新しい形式の`nr_setting`に変換するプログラム。

## How to use

1. `v3`をワーキングディレクトリにします。
2. `pip install -r requirements`で、必須モジュールをインストールします。
3. `temp.setting.json`を参考にして、必要な情報を`setting.json`に書き込みます。
4. `main.py`を実行します。
5. 生成された`writedata.json`を、MongoDBにインポートします。
