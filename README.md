# hw6

## アプリ

乗り換え案内はBFSで経路を出す（時間の表示はない．）

## make_graph.py (branch hw6-3)

`python make_graph.py`  
(networkxをインストールする必要があるかもしれない．)  

時間も表示したいと考え，時間情報をノードに入れたグラフ構造を考えた．  
グラフを作る時に，同じ路線で違う駅・違う路線で同じ駅（乗り換え駅）・同じ駅で違う時間のノードをつないだ．    
探索アルゴリズム自体は時間がなかったので`networkx`を使った．  =>  その結果，アプリで実行できず・・・  (import エラーが出る)  
乗り換え回数と最小時間での移動の探索を行えるようにした．  
アプリではないけれどやりたいことはできた！  
探索も自分で実装すればアプリにできると思う．  
（ただし，下の問題点を解決する必要がある．）


### 解決しなかったこと

グラフを作るとき，時間がたくさんかかってしまう．  
このままだと，検索中に電車が行ってしまうかも・・・ :)  

# hw6 template

1. Fork a repository for yourself with the github "Fork" button.
2. Clone your repository to your local machine.
3. Start a local AppEngine server with `dev_appserver.py go/` or `dev_appserver.py python/` (depending on whether you're using Go or Python).
4. Add functionality and test your App by viewing the local instance at http://localhost:8080
5. Deploy your app to AppEngine with `gcloud app deploy go/` or `gcloud app deploy python/`
    1. Note: the first time you do this, you'll have to first set up an AppEngine project via [Google Cloud Console](https://console.cloud.google.com/appengine/).
6. `git add .` and `git commit` and `git push` to upload your changes to your GitHub repository.
7. Send email to the STEP mailing list to show everyone your awesome App!

Feel free to repeat steps 3-7 as much as you like!
