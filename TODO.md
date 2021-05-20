# TODO

## NavSatFix でWayPoint指定 -> x, yを緯度経度に変換する必要  

msgファイル周りは弄らないようにしたい

## 弄るであろうファイル  
  
- /buttori_teleop/scripts/manual_logicool.py
- /buttori_main/captain_default.py  

## 流れ


```plantuml
:コントローラーのボタンを押す;
:jsonファイルを読み込む;
:waypoint取り出してcaptainに投げる;
:captainはコマンドを受け取ってミッション実行;
```

## 仕様

- jsonファイルを読み込んだら不正な値かどうかをチェックする  
  明らかに異常な値が設定されている(ex. waypointが1000m離れてる、不正な形式で渡されてる etc.)場合は弾く

- jsonを読み込んだ時点で一度可視化を行い、今行っているミッションがどのようなものか一目で分かるようにする  
  ミッション内容が事前に分かるためエラーをチェックできる

## TODO

コントローラーのボタン割り当て (LB, RB同時押しとか？)  
jsonファイルの読み込み部分の実装  
jsonファイルの可視化の実装(Python標準実装の tkinter)  

## json形式

- 必要な情報  
  position x, y  
  yaw角  
  margin  
  duration  
  timeout  
