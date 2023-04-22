# NIRA DB MGR
Nira bot database manager.

# Versions
結論：ブランチかレポジトリ分けろよ（大声）

- v1  
  pickleでの物理データ保存からHTTP_dbへの変換を行う際に使用するデータベース管理プログラム

- v2  
  HTTP_dbでのデータ保存からMongoDBへの変換 を行う際に使用するデータベース管理プログラム

# How to use
## v2
1. `cd ./v2`とかして、`./v2`をワーキングディレクトリにします。  
2. `pip install -r requirements`で、必須モジュールをインストールします。  
3. `temp.setting.json`を参考にして、必要な情報を`setting.json`に書き込みます。  
4. `main.py`を実行します。  
5. あとはご自由に。

## v1
（多分最初にワーキングディレクトリの変更しなきゃだめ）  
1. `pip install -r requirements`で、必須モジュールをインストールします。  
2. `temp.setting.json`を参考にして、データの管理をしたいにらBOTがあるディレクトリの場所を`setting.json`に書き込みます。  
3. `main.py`を実行します。  
4. あとはご自由に。
