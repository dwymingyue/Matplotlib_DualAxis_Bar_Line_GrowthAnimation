"""
作图主题：总量（条形图）+ 变化率（折线）双轴图（静态图 + 生长动画）
作者：陇上拾光, Kimi & 其他LLM
Python版本：3.12
最近修改时间：2026年2月12日
功能描述：在合适的时间序列数据中，绘制总量（条形图）和变化率（折线）的双Y轴组合图表；支持数据动态可视化（通过动画功能）
"""

# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
from matplotlib.animation import FuncAnimation

# 0. 参数表
CONFIG = {
    "file": "data.xlsx",  # Excel 路径
    "sheet": 3,  # 工作表，也可给字符串
    "col_year": "year",  # 年份列
    "col_stock": "y",  # 总量列（原始单位）
    "col_flow": "dy",  # 变化量列（原始单位）
    # 时间窗口（左右闭区间）
    "year_start": 1982,
    "year_end": 2024,
    # 单位换算 → 最终显示单位
    "stock_factor": 1,
    "flow_factor": 1,
    "stock_unit": "",
    "flow_unit": "%",
    # 轴范围 / 刻度
    "xlim_pad": 1,  # 左右留白
    "xtick_step": 6,  # 年份刻度步长
    "ylim_stock": (0, 6000),  # 左轴刻度
    "ytick_stock": np.arange(0, 6100, 600),
    "ylim_flow": (0, 20),  # 右轴刻度
    "ytick_flow": np.arange(0, 21, 2),
    # 颜色
    "color_stock": "#2f8cbf",
    "color_flow": "#e48e19",
    "highlight_color": "#236990",
    "highlight_years": {1982, 1990, 2000, 2010, 2020},
    # 图例文字
    "label_stock": "GDP定基指数，1978年 = 100（左轴）",
    "label_flow": "GDP增速，按不变价计算（右轴）",
    "legend_loc": "upper left",
    # 动画参数
    "k": 10,
    "base": 16,
    "interval": 42,
    # 标题 & 保存
    "title": "1982-2024年××省GDP增长情况",
    "save_path": Path(r"D:\Desktop\Figure.png"),
    "dpi": 600,
    "figsize": (10, 6.2),
}

# 全局字体设置
plt.rcParams["font.family"] = ["Times New Roman", "Simsun"]
plt.rcParams["font.size"] = 12
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.unicode_minus"] = False


# 1. 读取Excel数据
def load_data(cfg: dict) -> pd.DataFrame:
    df = (
        pd.read_excel(cfg["file"], sheet_name=cfg["sheet"])
        .loc[:, [cfg["col_year"], cfg["col_stock"], cfg["col_flow"]]]
        .dropna(subset=[cfg["col_year"], cfg["col_stock"]])
    )
    df[cfg["col_year"]] = df[cfg["col_year"]].astype(int)
    mask = (df[cfg["col_year"]] >= cfg["year_start"]) & (
        df[cfg["col_year"]] <= cfg["year_end"]
    )
    print(df.head(10))
    return df[mask].sort_values(cfg["col_year"])


'''


def load_data(cfg: dict) -> pd.DataFrame:
    """
    读取并清洗Excel数据。
    
    流程：读取指定工作表 -> 提取目标列 -> 剔除关键列的空值 -> 
          年份转整型 -> 根据起止年份过滤 -> 按年份排序返回。
    """
    try:
        # 使用链式调用简化初期清洗逻辑，减少零碎的赋值
        df = (
            pd.read_excel(cfg["file"], sheet_name=cfg["sheet"])
            .loc[:, [cfg["col_year"], cfg["col_stock"], cfg["col_flow"]]]
            .dropna(subset=[cfg["col_year"], cfg["col_stock"]])
        )
    except FileNotFoundError:
        raise FileNotFoundError(f"数据加载失败，找不到文件: {cfg['file']}")
    except KeyError as e:
        raise KeyError(f"配置文件中的列名在Excel中不存在: {e}")

    # 类型转换与筛选
    df[cfg["col_year"]] = df[cfg["col_year"]].astype(int)
    mask = (df[cfg["col_year"]] >= cfg["year_start"]) & (
        df[cfg["col_year"]] <= cfg["year_end"]
    )
    
    # 替代 print，使用 logging 或在调用该函数的外部去查看前10行
    logging.debug(f"数据加载完成，数据预览:\n{df.head()}")
    
    return df[mask].sort_values(cfg["col_year"])
'''


# 2. 绘图函数
def make_plot(df, cfg: dict):

    years = df[cfg["col_year"]].values
    stock = df[cfg["col_stock"]].values * cfg["stock_factor"]  # 单位换算
    flow = df[cfg["col_flow"]].values * cfg["flow_factor"]  # 单位换算

    fig, ax_bar = plt.subplots(figsize=cfg["figsize"])
    ax_line = ax_bar.twinx()

    # 条形图
    bars = ax_bar.bar(
        years,
        stock,
        color=cfg["color_stock"],
        width=0.5,
        zorder=2,
        label=cfg["label_stock"],
    )

    # 折线图
    ax_line.plot(
        years,
        flow,
        "-o",
        color=cfg["color_flow"],
        lw=2,
        markerfacecolor=cfg["color_flow"],
        markersize=3,
        zorder=3,
        label=cfg["label_flow"],
    )

    # 轴范围/刻度
    ax_bar.set_xlim(
        cfg["year_start"] - cfg["xlim_pad"], cfg["year_end"] + cfg["xlim_pad"]
    )
    ax_bar.set_xticks(
        np.arange(cfg["year_start"], cfg["year_end"] + 1, cfg["xtick_step"])
    )
    ax_bar.set_ylim(*cfg["ylim_stock"])
    ax_bar.set_yticks(cfg["ytick_stock"])
    ax_line.set_ylim(*cfg["ylim_flow"])
    ax_line.set_yticks(cfg["ytick_flow"])

    # 中文标签
    ax_bar.set_xlabel("年份")
    ax_bar.set_ylabel(cfg["stock_unit"])
    ax_line.set_ylabel(cfg["flow_unit"], rotation=0, labelpad=15)

    # 图例合并
    lines1, labels1 = ax_bar.get_legend_handles_labels()
    lines2, labels2 = ax_line.get_legend_handles_labels()
    leg = ax_bar.legend(
        lines1 + lines2,
        labels1 + labels2,
        frameon=True,
        edgecolor="black",
        loc=cfg["legend_loc"],
    )
    leg.get_frame().set_linewidth(0.6)

    for bar, year in zip(bars, years):
        if year in cfg["highlight_years"]:
            bar.set_color(cfg["highlight_color"])
    # 网格/边框
    ax_bar.grid(axis="y", ls="--", lw=0.5, color="gray", alpha=0.4)
    ax_bar.spines["top"].set_visible(False)
    ax_line.spines["top"].set_visible(False)

    # 标题（可选）
    fig.suptitle(cfg["title"])
    fig.tight_layout()
    cfg["save_path"].parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(cfg["save_path"], dpi=cfg["dpi"], bbox_inches="tight")
    print(f"✅ 已保存 → {cfg['save_path']}")
    plt.show()


# 3. 动画（先搭好一张静态画布，然后逐帧只改数据，把每一帧拼成视频）
def make_anim(df, cfg: dict):

    years = df[cfg["col_year"]].values
    stock = df[cfg["col_stock"]].values * cfg["stock_factor"]
    flow = df[cfg["col_flow"]].values * cfg["flow_factor"]
    n = len(years)

    # 画布与静态图完全一致
    fig, ax_bar = plt.subplots(figsize=cfg["figsize"])
    ax_line = ax_bar.twinx()

    # 与绘图保持一致
    ax_bar.set_xlim(
        cfg["year_start"] - cfg["xlim_pad"], cfg["year_end"] + cfg["xlim_pad"]
    )
    ax_bar.set_xticks(
        np.arange(cfg["year_start"], cfg["year_end"] + 1, cfg["xtick_step"])
    )
    ax_bar.set_ylim(*cfg["ylim_stock"])
    ax_bar.set_yticks(cfg["ytick_stock"])
    ax_line.set_ylim(*cfg["ylim_flow"])
    ax_line.set_yticks(cfg["ytick_flow"])

    ax_bar.set_xlabel("年份")
    ax_bar.set_ylabel(cfg["stock_unit"])
    ax_line.set_ylabel(cfg["flow_unit"], rotation=0, labelpad=15)

    # 一次建好所有 bar，高度先给 0
    bars = ax_bar.bar(
        years,
        np.zeros_like(stock),
        color=cfg["color_stock"],
        width=0.5,
        zorder=2,
        label=cfg["label_stock"],
    )

    # 一次建好折线，数据先空
    (line_dot,) = ax_line.plot(
        [],
        [],
        "-o",
        color=cfg["color_flow"],
        lw=2,
        markerfacecolor=cfg["color_flow"],
        markersize=3,
        zorder=3,
        label=cfg["label_flow"],
    )

    lines1, labels1 = ax_bar.get_legend_handles_labels()
    lines2, labels2 = ax_line.get_legend_handles_labels()
    leg = ax_bar.legend(
        lines1 + lines2,
        labels1 + labels2,
        frameon=True,
        edgecolor="black",
        loc=cfg["legend_loc"],
    )
    leg.get_frame().set_linewidth(0.6)

    # 高亮年份
    for bar, year in zip(bars, years):
        if year in cfg["highlight_years"]:
            bar.set_color(cfg["highlight_color"])

    ax_bar.grid(axis="y", ls="--", lw=0.5, color="gray", alpha=0.4)
    ax_bar.spines["top"].set_visible(False)
    ax_line.spines["top"].set_visible(False)
    # 标题（可选）
    fig.suptitle(cfg["title"])
    fig.tight_layout()

    k = cfg["k"]  # 一年分k步长出来，越大越慢
    slow_frames = n * k + 1  # 总帧数

    def grow_slow(frame):
        year_idx = min(frame // k, n - 1)  # 当前应该长到第几根
        ratio = (frame % k) / k if frame < n * k else 1.0  # 线性插值
        for idx in range(year_idx):
            bars[idx].set_height(stock[idx])  # 已完成的直接到顶
        if year_idx < n:  # 正在长的那根
            bars[year_idx].set_height(stock[year_idx] * ratio)
            bars[year_idx].set_y(0)

        flow_span = flow[year_idx] - cfg["base"]
        y_now = cfg["base"] + flow_span * ratio
        line_dot.set_data(
            years[: year_idx + 1] if frame else [],
            flow[: year_idx + 1] if ratio == 1 else np.append(flow[:year_idx], y_now),
        )
        return bars.patches + [line_dot]

    def init():
        for b in bars:
            b.set_height(0)
        line_dot.set_data([], [])
        return bars.patches + [line_dot]

    anim = FuncAnimation(
        fig,
        grow_slow,
        frames=slow_frames,
        init_func=init,
        interval=cfg["interval"],
        repeat=False,
        blit=True,
    )

    save_path = cfg["save_path"].with_name(cfg["save_path"].stem + "_grow.mp4")
    anim.save(save_path, writer="ffmpeg", dpi=cfg["dpi"])
    print(f"✅ 生长动画已保存 → {save_path}")
    plt.show()


# 4. 一键运行
df = load_data(CONFIG)
if __name__ == "__main__":
    make_plot(df, CONFIG)
    # make_anim(df, CONFIG)
