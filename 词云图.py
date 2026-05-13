# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from pyecharts.charts import WordCloud
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import jieba
from collections import Counter

# ========== 1. 添加汽车领域自定义词典 ==========
# 防止 jieba 将专业术语错误切分
custom_terms = [
    "智能驾驶", "辅助驾驶", "自动泊车", "车机系统", "智能座舱",
    "语音助手", "语音控制", "安全配置", "安全系数", "充电速度",
    "后排空间", "底盘质感", "驾驶质感", "乘坐舒适", "悬挂舒适",
    "底盘舒适", "静谧性", "达成率", "城市NGP", "流线型",
    "做工精致", "加速迅猛", "加速超快", "刹车线性", "变道顺滑", "操控灵活",
    "用料环保", "风噪控制", "品牌力", "品牌力强", "换电方便", "续航扎实",
    "做工扎实", "颜值高", "颜值超高", "性价比高", "智能化", "极简内饰",
    "内饰高级", "内饰简约", "外观帅气", "外观优雅", "空间够用",
    "驾驶感受", "服务超好", "续航达成率"
]
for term in custom_terms:
    jieba.add_word(term)

# ========== 2. 读取评价数据并分词 ==========
df_reviews = pd.read_csv("reviews_text.csv")
all_text = " ".join(df_reviews["评价内容"].tolist())
words = jieba.lcut(all_text)

# ========== 3. 停用词过滤与词频统计 ==========
stopwords = {"很", "非常", "不错", "不", "没", "也", "还", "更", "比较", "有点"}
word_counts = Counter(
    w.strip() for w in words
    if len(w.strip()) >= 2 and w not in stopwords
)

# ========== 4. 对数平滑处理 ==========
freq_values = list(word_counts.values())
max_freq = max(freq_values)
min_freq = min(freq_values)
ratio = max_freq / min_freq if min_freq > 0 else float("inf")

print(f"词频最大值: {max_freq}, 最小值: {min_freq}, 比值: {ratio:.2f}")

log_smoothed = ratio > 100
if log_smoothed:
    print("比值超过100倍，进行对数平滑处理...")
    word_counts_smoothed = {w: np.log1p(c) for w, c in word_counts.items()}
else:
    word_counts_smoothed = dict(word_counts)
    print("比值未超过100倍，无需平滑处理。")

# ========== 5. 转换为 pyecharts 数据格式 ==========
sorted_words = sorted(word_counts_smoothed.items(), key=lambda x: x[1], reverse=True)[:200]
data_pair = [(word, round(freq, 2)) for word, freq in sorted_words]

# ========== 6. 使用 pyecharts 生成词云图 ==========
wc = (
    WordCloud(init_opts=opts.InitOpts(width="1000px", height="600px", theme=ThemeType.WHITE))
    .add(
        series_name="",
        data_pair=data_pair,
        word_size_range=[14, 72],
        shape="circle",
        word_gap=6,
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="汽车评价词云图", pos_left="center",
                                  title_textstyle_opts=opts.TextStyleOpts(font_size=20)),
        tooltip_opts=opts.TooltipOpts(is_show=True),
    )
)

wc.render("词云图.html")
print(f"词云生成完毕，有效词语: {len(word_counts)} 个，已保存为 词云图.html")
