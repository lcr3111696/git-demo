import pandas as pd
import matplotlib
matplotlib.use("Agg")          # 不弹窗，直接存文件；必须写在 pyplot 之前
import matplotlib.pyplot as plt

# ---------- 1. 读数据 ----------
df = pd.read_csv("600519_daily.csv", encoding="utf-8-sig")
df["日期"] = pd.to_datetime(df["日期"])
df = df.sort_values("日期").reset_index(drop=True)

# ---------- 2. 算均线 ----------
df["MA5"]  = df["收盘"].rolling(5).mean()
df["MA20"] = df["收盘"].rolling(20).mean()

print(df[["日期", "收盘", "MA5", "MA20"]].head(6).to_string())
print(df[["日期", "收盘", "MA5", "MA20"]].tail(3).to_string())

# ---------- 3. 画图 ----------
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]   # 中文显示
plt.rcParams["axes.unicode_minus"] = False              # 负号正常显示

fig, ax = plt.subplots(figsize=(11, 5), dpi=150)

ax.plot(df["日期"], df["收盘"], label="收盘价", color="#555555", linewidth=0.9)
ax.plot(df["日期"], df["MA5"],  label="MA5",  color="#e74c3c", linewidth=1.2)
ax.plot(df["日期"], df["MA20"], label="MA20", color="#2980b9", linewidth=1.5)

ax.set_title("贵州茅台 600519 日收盘价与 5/20 日均线（2024）")
ax.set_xlabel("日期")
ax.set_ylabel("价格（元，前复权）")
ax.legend(loc="upper right")
ax.grid(alpha=0.3)

fig.autofmt_xdate()            # 日期斜着排，避免挤在一起
fig.tight_layout()
fig.savefig("ma.png", bbox_inches="tight")\

ma5, ma20 = df["MA5"].iloc[-1], df["MA20"].iloc[-1]
print(f"最后交易日 {df['日期'].iloc[-1].date()}  MA5={ma5:.2f}  MA20={ma20:.2f}  "
      f"MA5-MA20={ma5-ma20:+.2f} → {'MA5 在上（多头）' if ma5 > ma20 else 'MA5 在下（空头）'}")
print("已保存 ma.png")