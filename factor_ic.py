import pandas as pd

df = pd.read_csv("hs300_50_daily.csv", encoding="utf-8-sig")
df["日期"] = pd.to_datetime(df["日期"])

# 1. 宽表：行=日期，列=股票
close = df.pivot(index="日期", columns="股票代码", values="收盘")
print("宽表形状:", close.shape)          # (242, 48)

# 2. 因子（今天就能算）：过去 5 日涨幅
r5 = close / close.shift(5) - 1

# 3. 未来 5 日收益（今天还不知道）
fwd = close.shift(-5) / close - 1

# 4. 逐日 Rank IC
ic = r5.corrwith(fwd, axis=1, method="spearman").dropna()

# 5. 四个数
print(f"样本天数 : {len(ic)} 天")
print(f"IC 均值  : {ic.mean():.4f}")
print(f"IC 标准差: {ic.std():.4f}")
print(f"ICIR     : {ic.mean() / ic.std():.3f}")
print(f"IC>0 占比: {(ic > 0).mean():.1%}")