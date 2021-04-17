# ロボットのミッションファイル作る用のGUI

## 機能  

グラフ上をクリックでウェイポイント追加可能  
ウェイポイント上で右クリックでその点を削除  
undo, repeat, clear機能  
座標指定でのウェイポイント追加  
jsonファイルでwaypointを出力

## exp  

mission.json  

```json
{
  "waypoints": [
    {
      "ID": 0,
      "X": 0.0,
      "Y": 0.0,
      "Z": 15.0
    },
    {
      "ID": 1,
      "X": 0.0,
      "Y": 20.0,
      "Z": 15.0
    },
    {
      "ID": 2,
      "X": 5.0,
      "Y": 20.0,
      "Z": 15.0
    },
    {
      "ID": 3,
      "X": 5.0,
      "Y": 0.0,
      "Z": 15.0
    },
    {
      "ID": 4,
      "X": 10.0,
      "Y": 0.0,
      "Z": 15.0
    },
    {
      "ID": 5,
      "X": 10.0,
      "Y": 20.0,
      "Z": 15.0
    },
    {
      "ID": 6,
      "X": 15.0,
      "Y": 20.0,
      "Z": 15.0
    },
    {
      "ID": 7,
      "X": 15.0,
      "Y": 0.0,
      "Z": 15.0
    },
    {
      "ID": 8,
      "X": 20.0,
      "Y": 0.0,
      "Z": 15.0
    },
    {
      "ID": 9,
      "X": 20.0,
      "Y": 20.0,
      "Z": 15.0
    },
    {
      "ID": 10,
      "X": 25.0,
      "Y": 20.0,
      "Z": 15.0
    },
    {
      "ID": 11,
      "X": 25.0,
      "Y": 0.0,
      "Z": 15.0
    },
    {
      "ID": 12,
      "X": 30.0,
      "Y": 0.0,
      "Z": 15.0
    },
    {
      "ID": 13,
      "X": 30.0,
      "Y": 20.0,
      "Z": 15.0
    },
    {
      "ID": 14,
      "X": 35.0,
      "Y": 20.0,
      "Z": 15.0
    },
    {
      "ID": 15,
      "X": 35.0,
      "Y": 0.0,
      "Z": 15.0
    },
    {
      "ID": 16,
      "X": 40.0,
      "Y": 0.0,
      "Z": 15.0
    }
  ]
}
```

![example image1](https://raw.githubusercontent.com/satoshi-teji/mission_generator/master/image/way1.PNG)  
![example image2](https://raw.githubusercontent.com/satoshi-teji/mission_generator/master/image/way2.PNG)  
