import sys 
import time 
import ccxt
from datetime import datetime
from pprint import pprint

print(datetime.now())

#パラメータ===============================
GOAL = 100000
LEVE = 10
print("deffence", 100/(LEVE+1), "%")
LOT = 100
STIME = 3
bybit = ccxt.bybit()
bybit.apiKey = ""
bybit.sercret = ""

#初期設定================================
#全注文キャンセル
bybit.cancel_all_orders("BTC/USD")
#証拠金を取得
res = bybit.fetch_balance()
#ポジションを取得
pos = bybit.v2PrivateGetPositionList({"symbol":"BTCUSD"})
balance = float(res["BTC"]["free"]) + float(res["BTC"]["used"]) + float(pos["result"]["unrealised_pnl"])
print("balance+unreal:", balance, "BTC")
print("pos", pos["result"]["size"], "USD")
#決済指値注文
if pos["result"]["size"] > 0:
    order = bybit.v2PrivatePostOrderCreate({
        "side" : "sell",
        "symbol": "sell",
        "order_type": "Limit",
        "qty": pos["result"]["size"],
        "price": GOAL,
        "time_in_force": "PostOnly",
        "reduce_only" : True
    })
#寸前のポジション，減ったら決済
pre_pos = pos["result"]["size"]

while True:
    try:
        #証拠金を取得
        res = bybit.fetch_balance()
        #ポジションを取得
        pos = bybit.v2PrivateGetPositionList({"symbol":"BTCUSD"})
        balance = float(res["BTC"]["free"]) + float(res["BTC"]["used"]) + float(pos["result"]["unrealised_pnl"])
        #レバレッジ計算
        margin_leve = float(pos["result"]["position_value"]) / balance
        #ポジション量が減少したら決済スタートorストップ
        if pos["result"]["size"] < pre_pos:
            print("DECLEASE POS")
            break
        #基準レバレッジを下回ればポジション増加
        if margin_leve < LEVE:
            print(datetime.now())
            print("LONG (leve", margin_leve, ")" )
            res = bybit.create_market_buy_order("BTC/USD", LOT)

            print("pos", pos["result"]["size"], "USD")
            res = bybit.v2PrivatePostOrderReplace({
                "order_id": order["result"]["order_id"],
                "symbol" : "BTCUSD",
                "p_r_qty" : pos["result"]["size"] + LOT
            })
    except Exception as e:
        print(datetime.now())
        print(e)
    time.sleep(STIME)
    pre_pos = pos["result"]["size"]
