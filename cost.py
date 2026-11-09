import pandas as pd

# ============ 费率参数（要写进 README）============
COMMISSION = 0.00025   # 佣金 万2.5，双边
STAMP_DUTY = 0.0005    # 印花税 0.05%，仅卖出
SLIPPAGE   = 0.0005    # 滑点 0.05%，单边

COST_BUY  = COMMISSION + SLIPPAGE                # 0.075%
COST_SELL = COMMISSION + STAMP_DUTY + SLIPPAGE   # 0.125%

# ============ 策略（复用 T1.4）============
df = pd.read_csv("600519_daily.csv", encoding="utf-8-sig")
df["日期"] = pd.to_datetime(df["日期"])
df = df.sort_values("日期").reset_index(drop=True)

df["MA5"]  = df["收盘"].rolling(5).mean()
df["MA20"] = df["收盘"].rolling(20).mean()
df["signal"] = (df["MA5"] > df["MA20"]).astype(int)
df["pos"]    = df["signal"].shift(1)
df["ret"]    = df["收盘"].pct_change()
df["strategy"] = (df["pos"] * df["ret"]).fillna(0)

# ============ 只在换仓那天扣费 ============
df["chg"]  = df["pos"].diff().fillna(0)          # +1 买入 / -1 卖出 / 0 不动
df["cost"] = (df["chg"] > 0) * COST_BUY + (df["chg"] < 0) * COST_SELL
df["net"]  = df["strategy"] - df["cost"]

def total(s):
    return (1 + s).cumprod().iloc[-1] - 1

gross = total(df["strategy"])
net   = total(df["net"])

n_buy  = int((df["chg"] > 0).sum())
n_sell = int((df["chg"] < 0).sum())
trades = n_buy + n_sell
avg_cost = df["cost"].sum() / trades

print(f"不含费累计收益 : {gross:+.2%}")
print(f"含费累计收益   : {net:+.2%}")
print(f"费用拖累       : {(gross - net) * 100:.2f} pp")
print(f"换手次数       : {trades} 次（买 {n_buy} / 卖 {n_sell}）")
print(f"单次平均成本   : {avg_cost:.3%}")
print(f"结论：费用让我多亏了 {(gross-net)*100:.2f} 个百分点，"
      f"占总亏损的 {(gross-net)/abs(net)*100:.1f}%")

# ============ 成本敏感性（加分项）============
print("\n--- 成本敏感性 ---")
for rate in (0.00075, 0.002, 0.004):
    c = (df["chg"] != 0) * rate
    r = total(df["strategy"] - c)
    print(f"单边 {rate:.2%} → 累计收益 {r:+.2%}，拖累 {(gross - r) * 100:.2f} pp")