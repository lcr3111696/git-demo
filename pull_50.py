import time
import pandas as pd
import akshare as ak

START, END = "20240101", "20241231"

# ---------- 1. 成分股（关键：去重）----------
cons = ak.index_stock_cons(symbol="000300")
print("原始名单:", len(cons), "行，去重后:", cons["品种代码"].nunique())
cons = cons.drop_duplicates(subset="品种代码").reset_index(drop=True)
codes = cons["品种代码"].head(50).tolist()
name_map = cons.set_index("品种代码")["品种名称"]

# ---------- 2. 逐只拉取 ----------
frames, failed = [], []
for i, code in enumerate(codes, 1):
    try:
        d = ak.stock_zh_a_hist(symbol=code, period="daily",
                               start_date=START, end_date=END, adjust="qfq")
        if d is None or d.empty:
            failed.append(code)
            continue
        frames.append(d)
    except Exception as e:
        failed.append(code)
        print(f"{code} 拉取失败: {e}")
    time.sleep(0.2)
    if i % 10 == 0:
        print(f"进度 {i}/{len(codes)}")

df = pd.concat(frames, ignore_index=True)
df["日期"] = pd.to_datetime(df["日期"])

# ---------- 3. 体检 ----------
print("\nshape:", df.shape)
print("股票数:", df["股票代码"].nunique())
print("duplicated:", df.duplicated(subset=["股票代码", "日期"]).sum())
print("每只行数分布:\n", df.groupby("股票代码").size().value_counts().to_string())
print("拉取失败:", failed)

short = df.groupby("股票代码").size()
short = short[short < 242]
print("\n不足 242 行的股票:")
for c, n in short.items():
    sub = df[df["股票代码"] == c]
    print(f"  {c} {name_map.get(c, '')}: {n} 行  "
          f"{sub['日期'].min().date()} ~ {sub['日期'].max().date()}")

# ---------- 4. 2024-12-31 的 5 日收益 ----------
df = df.sort_values(["股票代码", "日期"])
df["r5"] = df.groupby("股票代码")["收盘"].pct_change(5)

day = df[df["日期"] == pd.Timestamp("2024-12-31")].dropna(subset=["r5"]).copy()
day["名称"] = day["股票代码"].map(name_map)

print("\nTOP5")
print(day.nlargest(5, "r5")[["股票代码", "名称", "r5"]].to_string(index=False))
print("\nBOTTOM5")
print(day.nsmallest(5, "r5")[["股票代码", "名称", "r5"]].to_string(index=False))

# ---------- 5. 落盘 ----------
df.to_csv("hs300_50_daily.csv", index=False, encoding="utf-8-sig")
print("\n已保存 hs300_50_daily.csv")