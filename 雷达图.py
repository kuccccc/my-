# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from pyecharts.charts import Radar
from pyecharts import options as opts

# ========== 1. 读取数据 ==========
df_cars = pd.read_csv("car_evaluation.csv")
cars = df_cars["车型"].tolist()
dimensions = ["续航里程", "快充速度", "智能驾驶", "空间舒适", "价格竞争力", "安全评分"]
display_dimensions = ["续航(km)"] + dimensions[1:]

# 5款车配色
colors = ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6"]

# ========== 2. 数据预处理 ==========
# 续航里程除以10归一化至0-100评分制
car_data = []
for i, car in enumerate(cars):
    vals = df_cars[df_cars["车型"] == car][dimensions].values[0].tolist()
    vals[0] = round(vals[0] / 10, 1)  # 续航归一化
    car_data.append((car, vals, colors[i]))

# ========== 3. 构建雷达图 schema ==========
schema = [opts.RadarIndicatorItem(name=dim, max_=100) for dim in display_dimensions]

# ========== 4. 绘制雷达图 ==========
radar = Radar(init_opts=opts.InitOpts(width="1000px", height="800px"))

radar.add_schema(
    schema=schema,
    shape="circle",
    radius="75%",
    center=["50%", "52%"],
    splitarea_opt=opts.SplitAreaOpts(is_show=False),
)

for car_name, vals, color in car_data:
    radar.add(
        series_name=car_name,
        data=[vals],
        color=color,
        areastyle_opts=opts.AreaStyleOpts(opacity=0.12),
        linestyle_opts=opts.LineStyleOpts(width=2.5),
        symbol="circle",
        label_opts=opts.LabelOpts(is_show=False),
    )

# ========== 5. 布局配置 ==========
radar.set_global_opts(
    title_opts=opts.TitleOpts(
        title="新能源车型六维对比雷达图",
        pos_left="center",
        title_textstyle_opts=opts.TextStyleOpts(font_size=20),
    ),
    legend_opts=opts.LegendOpts(
        orient="horizontal",
        pos_bottom="0%",
        pos_left="center",
    ),
    tooltip_opts=opts.TooltipOpts(trigger="item"),
)

radar.render("雷达图.html")
print("雷达图 HTML 已生成，保存为 雷达图.html")
