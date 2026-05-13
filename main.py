# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import plotly.graph_objects as go
import jieba
import base64
import io
from collections import Counter

# ========== 1. 读取数据 ==========
df_cars = pd.read_csv('car_evaluation.csv')
cars = df_cars['车型'].tolist()
dimensions = ['续航里程', '快充速度', '智能驾驶', '空间舒适', '价格竞争力', '安全评分']
display_dimensions = ['续航(km)'] + dimensions[1:]

# 5款车配色
colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6']
transparent_fills = [
    'rgba(231,76,60,0.12)', 'rgba(52,152,219,0.12)', 'rgba(46,204,113,0.12)',
    'rgba(243,156,18,0.12)', 'rgba(155,89,182,0.12)'
]

# 准备数据：续航里程除以10归一化至0-100评分制
car_data = []
for i, car in enumerate(cars):
    vals = df_cars[df_cars['车型'] == car][dimensions].values[0].tolist()
    vals[0] = round(vals[0] / 10, 1)
    car_data.append((car, vals, colors[i], transparent_fills[i]))

# 构建统一 hover 文本
unified_hover = [
    "<br>".join([f"<b>{dim}</b>"] + [f"{car}: {vals[d]}" for car, vals, _, _ in car_data])
    for d, dim in enumerate(display_dimensions)
]
unified_hover_closed = unified_hover + [unified_hover[0]]

# ========== 2. 绘制雷达图 ==========
fig = go.Figure()
dims_closed = display_dimensions + [display_dimensions[0]]
for car_name, vals, color, fill_color in car_data:
    fig.add_trace(go.Scatterpolar(
        r=vals + [vals[0]], theta=dims_closed, name=car_name,
        fill='toself', fillcolor=fill_color,
        line=dict(color=color, width=2.5),
        marker=dict(color=color, size=10, symbol='circle'),
        mode='lines+markers',
        hoveron='points+fills',
        opacity=0.9,
        customdata=unified_hover_closed,
        hovertemplate='%{customdata}<extra></extra>'
    ))

fig.update_layout(
    polar=dict(
        gridshape='circular',
        radialaxis=dict(range=[0, 100], showticklabels=True, ticks=''),
        angularaxis=dict(rotation=90, direction='clockwise')
    ),
    title=dict(text='新能源车型六维对比雷达图', x=0.5, font=dict(size=20, family='MiSans')),
    legend=dict(orientation='h', y=-0.15, x=0.5, xanchor='center', font=dict(size=12, family='MiSans')),
    template='plotly_white',
    width=750, height=700,
    margin=dict(t=60, b=80, l=50, r=50),
    dragmode=False,
    hoverdistance=80
)

config = {
    'scrollZoom': False,
    'displayModeBar': True,
    'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d'],
    'displaylogo': False
}
radar_html = fig.to_html(include_plotlyjs='cdn', full_html=False, config=config)

# ========== 3. 词频统计 ==========
# 添加汽车领域术语，避免被 jieba 拆散
for term in ['智能驾驶', '辅助驾驶', '自动泊车', '车机系统', '智能座舱',
             '语音助手', '语音控制', '安全配置', '安全系数', '充电速度',
             '后排空间', '底盘质感', '驾驶质感', '乘坐舒适', '悬挂舒适',
             '底盘舒适', '静谧性', '达成率', '城市NGP', '流线型',
             '做工精致', '加速迅猛', '加速超快', '刹车线性', '变道顺滑', '操控灵活',
             '用料环保', '风噪控制', '品牌力', '品牌力强', '换电方便', '续航扎实',
             '做工扎实', '颜值高', '颜值超高', '性价比高', '智能化', '极简内饰',
             '内饰高级', '内饰简约', '外观帅气', '外观优雅', '空间够用',
             '驾驶感受', '服务超好', '续航达成率']:
    jieba.add_word(term)

df_reviews = pd.read_csv('reviews_text.csv')
all_text = ' '.join(df_reviews['评价内容'].tolist())
words = jieba.lcut(all_text)

stopwords = {'很', '非常', '不错', '不', '没', '也', '还', '更', '比较', '有点'}

word_counts = Counter(w.strip() for w in words if len(w.strip()) >= 2 and w not in stopwords)

# ========== 4. 对数平滑处理 ==========
freq_values = list(word_counts.values())
max_freq = max(freq_values)
min_freq = min(freq_values)
ratio = max_freq / min_freq if min_freq > 0 else float('inf')

print(f"词频最大值: {max_freq}, 最小值: {min_freq}, 比值: {ratio:.2f}")

log_smoothed = ratio > 100
if log_smoothed:
    print("比值超过100倍，进行对数平滑处理...")
    raw_top10 = word_counts.most_common(10)
    word_counts_smoothed = {w: np.log1p(c) for w, c in word_counts.items()}
    smooth_top10 = sorted(word_counts_smoothed.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"  平滑前 Top10: {raw_top10}")
    print(f"  平滑后 Top10: {smooth_top10}")
else:
    word_counts_smoothed = dict(word_counts)
    print("比值未超过100倍，无需平滑处理。")

# ========== 5. 生成词云 ==========
wc = WordCloud(
    font_path='C:/Windows/Fonts/MiSans-Regular.otf',
    width=1000, height=600,
    background_color='white',
    max_words=200, collocations=False,
    colormap='viridis'
).generate_from_frequencies(word_counts_smoothed)

buf = io.BytesIO()
wc.to_image().save(buf, format='PNG')
buf.seek(0)
wordcloud_b64 = base64.b64encode(buf.read()).decode('utf-8')
buf.close()

# ========== 6. 合并 HTML  ==========
combined_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>雷达图、词云图作业</title>
<script src="https://cdn.plot.ly/plotly-3.0.1.min.js"></script>
<style>
    @font-face {{
        font-family: 'MiSans';
        src: local('MiSans');
    }}
    body {{ font-family: 'MiSans', 'Microsoft YaHei', sans-serif; background: #f0f2f5; margin: 0; padding: 24px; }}
    .container {{ max-width: 1400px; margin: 0 auto; }}
    .header {{ text-align: center; margin-bottom: 24px; }}
    .header h1 {{ font-size: 28px; color: #1a1a2e; margin: 0; }}
    .header p {{ color: #888; font-size: 14px; margin-top: 6px; }}
    .row {{ display: flex; gap: 20px; align-items: stretch; flex-wrap: wrap; }}
    .card {{ background: white; border-radius: 14px; box-shadow: 0 2px 16px rgba(0,0,0,0.06); padding: 24px; }}
    .card h2 {{ text-align: center; color: #333; margin: 0 0 16px 0; font-size: 18px; }}
    .radar-card {{ flex: 1 1 780px; min-width: 620px; }}
    .wordcloud-card {{ flex: 1 1 500px; min-width: 400px; display: flex; flex-direction: column; align-items: center; }}
    .wordcloud-card img {{ max-width: 100%; height: auto; border-radius: 8px; }}
    .stats {{ display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-top: 16px; color: #555; font-size: 13px; }}
    .stats span {{ background: #f0f2f5; padding: 5px 16px; border-radius: 20px; }}
</style>
</head>
<body>
<div class="container">
<div class="header">
    <h1>雷达图、词云图作业</h1>
    <p>分析车型：{', '.join(cars)}  |  数据维度：续航、快充、智驾、空间、价格、安全</p>
</div>
<div class="row">

<div class="card radar-card">
    <h2>六维对比雷达图</h2>
    {radar_html}
</div>

<div class="card wordcloud-card">
    <h2>车主评价词云</h2>
    <img src="data:image/png;base64,{wordcloud_b64}" alt="词云图">
    <div class="stats">
        <span>评价条数：{len(df_reviews)}</span>
        <span>有效词语：{len(word_counts)}</span>
        <span>词频比值：{ratio:.1f}</span>
        <span>对数平滑：{'是' if log_smoothed else '否'}</span>
    </div>
</div>

</div>
</div>
</body>
</html>'''

with open('雷达图词云图作业.html', 'w', encoding='utf-8') as f:
    f.write(combined_html)
print("HTML 已保存为 雷达图词云图作业.html")