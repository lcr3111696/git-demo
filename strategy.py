import pandas as pd

pd.set_option("display.unicode.east_asian_width", True)

# ---------- 1. 数据 ----------
df = pd.read_csv("600519_daily.csv", encoding="utf-8-sig")
df["日期"] = pd.to_datetime(df["日期"])
df = df.sort_values("日期").reset_index(drop=True)

# ---------- 2. 均线 ----------
df["MA5"] = df["收盘"].rolling(5).mean()
df["MA20"] = df["收盘"].rolling(20).mean()

# ---------- 3. 信号与仓位 ----------
df["signal"] = (df["MA5"] > df["MA20"]).astype(int)   # 今天收盘算出的信号
df["pos"] = df["signal"].shift(1)                     # ← 灵魂：昨天收盘的信号，今天才生效
df["ret"] = df["收盘"].pct_change()
df["strategy"] = df["pos"] * df["ret"]

# ---------- 4. 指标 ----------
def total(s):
    return (1 + s.fillna(0)).cumprod().iloc[-1] - 1

r_correct = total(df["strategy"])
r_bh = total(df["ret"])
r_wrong = total(df["signal"] * df["ret"])   # 错误版：删掉 shift(1)

trades = (df["pos"].diff().fillna(0) != 0).sum()
hold = int(df["pos"].fillna(0).sum())

# ---------- 5. 打印 ----------
print(f"策略累计收益   : {r_correct:+.2%}")
print(f"买入持有       : {r_bh:+.2%}")
print(f"超额           : {r_correct - r_bh:+.2%}")
print(f"调仓次数       : {trades}")
print(f"持仓天数       : {hold} / {len(df)}")

print("\n--- 错误版（去掉 shift(1)，未来函数）---")
print(f"错误版累计收益 : {r_wrong:+.2%}")
print(f"比正确版虚高   : {r_wrong - r_correct:+.2%}")