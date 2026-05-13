import csv
import json
from pyecharts import options as opts
from pyecharts.charts import Scatter, EffectScatter
from pyecharts.commons.utils import JsCode

# ==================== 1. 从 CSV 读取数据 ====================
with open("food_data.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

groups = {}
for r in rows:
    groups.setdefault(r["类别"], []).append(r)

# 用 float 格式化 key，保证和 JS .toFixed(1) 一致
name_by_coord = {}
for r in rows:
    x = float(r["蛋白质含量_g_100g"])
    y = float(r["价格_元_500g"])
    key = f"{x:.1f}_{y:.1f}"
    name_by_coord[key] = r["食品名称"]

# ==================== 2. 颜色映射 ====================
color_map = {
    "肉类":   "#d94e5d",
    "蛋奶类": "#fac858",
    "豆类":   "#5470c6",
    "海鲜类": "#91cc75",
    "坚果类": "#ee6666",
}

# ==================== 3. 构建主 Scatter ====================
scatter = Scatter()
for cat, items in groups.items():
    x = [float(r["蛋白质含量_g_100g"]) for r in items]
    y = [float(r["价格_元_500g"]) for r in items]
    scatter.add_xaxis(x)
    scatter.add_yaxis(
        series_name=cat,
        y_axis=y,
        symbol_size=14,
        itemstyle_opts=opts.ItemStyleOpts(color=color_map[cat]),
        label_opts=opts.LabelOpts(is_show=False),
    )

# ==================== 4. TOP5 涟漪高亮 ====================
sorted_by_protein = sorted(rows, key=lambda r: float(r["蛋白质含量_g_100g"]), reverse=True)
top5 = sorted_by_protein[:5]

es = EffectScatter()
es.add_xaxis([float(r["蛋白质含量_g_100g"]) for r in top5])
es.add_yaxis(
    series_name="TOP5 高蛋白",
    y_axis=[float(r["价格_元_500g"]) for r in top5],
    symbol_size=18,
    effect_opts=opts.EffectOpts(scale=4.0, brush_type="fill"),
    itemstyle_opts=opts.ItemStyleOpts(color="#ff4757"),
    label_opts=opts.LabelOpts(
        is_show=True,
        position="top",
        formatter=JsCode(
            """function(p) {
                var key = p.data[0].toFixed(1) + '_' + p.data[1].toFixed(1);
                return foodNameMap[key] || '';
            }"""
        ),
        font_size=10,
    ),
)

# ==================== 5. 叠加 + 注入名称映射 ====================
scatter.overlap(es)
scatter.add_js_funcs(
    "var foodNameMap = " + json.dumps(name_by_coord, ensure_ascii=False) + ";"
)

# ==================== 6. 全局配置 ====================
scatter.set_global_opts(
    title_opts=opts.TitleOpts(
        title="常见食品：蛋白质含量 vs 价格",
        pos_left="center",
    ),
    xaxis_opts=opts.AxisOpts(
        name="蛋白质含量 (g/100g)",
        type_="value",
        splitline_opts=opts.SplitLineOpts(is_show=True),
    ),
    yaxis_opts=opts.AxisOpts(
        name="价格 (元/500g)",
        type_="value",
        splitline_opts=opts.SplitLineOpts(is_show=True),
    ),
    legend_opts=opts.LegendOpts(pos_bottom="0%"),
    visualmap_opts=opts.VisualMapOpts(
        type_="continuous",
        min_=0,
        max_=40,
        dimension=0,
        range_color=["#f0f0f0", "#1890ff", "#d4380d"],
        range_text=["高蛋白", "低蛋白"],
        pos_right=10,
        pos_top=60,
        orient="vertical",
    ),
    tooltip_opts=opts.TooltipOpts(
        trigger="item",
        formatter=JsCode(
            """function(p) {
                var key = p.data[0].toFixed(1) + '_' + p.data[1].toFixed(1);
                var name = foodNameMap[key] || '';
                return '<b>' + name + '</b><br/>'
                     + '类别：' + p.seriesName + '<br/>'
                     + '蛋白质：' + p.data[0] + ' g<br/>'
                     + '价格：' + p.data[1] + ' 元';
            }"""
        ),
    ),
)

# ==================== 7. 输出 ====================
scatter.render("图表.html")
print("图表已生成：图表.html")
print(f"数据点：{len(rows)} 条 | 分组：{len(groups)} 类 | TOP5：{[r['食品名称'] for r in top5]}")
