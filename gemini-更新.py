# -*- coding: utf-8 -*-
"""
优化后的GDP数据可视化脚本
功能：绘制双轴图（柱状图+折线图）及生成生长动画
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from typing import Tuple

# 0. 参数表
CONFIG = {
    "file": "data.xlsx",  # Excel 路径
    "sheet": 3,  # 工作表
    "col_year": "year",  # 年份列
    "col_stock": "y",  # 总量列
    "col_flow": "dy",  # 变化量列
    # 时间窗口
    "year_start": 1982,
    "year_end": 2024,
    # 单位换算
    "stock_factor": 1,
    "flow_factor": 1,
    "stock_unit": "",
    "flow_unit": "%",
    # 轴范围 / 刻度
    "xlim_pad": 1,
    "xtick_step": 6,
    "ylim_stock": (0, 6000),
    "ytick_stock": np.arange(0, 6100, 600),
    "ylim_flow": (0, 20),
    "ytick_flow": np.arange(0, 21, 2),
    # 颜色与样式
    "color_stock": "#2f8cbf",
    "color_flow": "#e48e19",
    "highlight_color": "#236990",
    "highlight_years": {1982, 1990, 2000, 2010, 2020},
    # 图例文字
    "label_stock": "GDP定基指数，1978年 = 100（左轴）",
    "label_flow": "GDP增速，按不变价计算（右轴）",
    "legend_loc": "upper left",
    # 动画参数
    "k": 10,  # 单根柱子生长的帧数
    "base": 16,  # 动画中折线生长的基准位置（视觉优化）
    "interval": 42,  # 帧间隔(ms)
    # 输出设置
    "title": "1982-2024年甘肃省GDP增长情况",
    "save_path": Path(r"D:\Desktop\figure.png"),
    "dpi": 600,
    "figsize": (10, 6.2),
}

# 全局字体设置
plt.rcParams["font.family"] = ["Times New Roman", "SimSun"]
plt.rcParams["font.size"] = 12
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.unicode_minus"] = False


def load_data(cfg: dict) -> pd.DataFrame:
    """读取并清洗Excel数据"""
    try:
        df = pd.read_excel(cfg["file"], sheet_name=cfg["sheet"])
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到文件: {cfg['file']}")

    # 提取列并去空
    cols = [cfg["col_year"], cfg["col_stock"], cfg["col_flow"]]
    df = df.loc[:, cols].dropna(subset=[cfg["col_year"], cfg["col_stock"]])

    # 类型转换与筛选
    df[cfg["col_year"]] = df[cfg["col_year"]].astype(int)
    mask = (df[cfg["col_year"]] >= cfg["year_start"]) & (
        df[cfg["col_year"]] <= cfg["year_end"]
    )

    df_clean = df[mask].sort_values(cfg["col_year"])
    print(f"数据加载完成，共 {len(df_clean)} 条记录。")
    return df_clean


def _setup_axes(ax_bar: Axes, ax_line: Axes, cfg: dict) -> None:
    # 1. 设置轴范围与刻度
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

    # 2. 标签
    ax_bar.set_xlabel("年份")
    ax_bar.set_ylabel(cfg["stock_unit"])
    ax_line.set_ylabel(cfg["flow_unit"], rotation=0, labelpad=15)

    # 3. 样式美化
    ax_bar.grid(axis="y", ls="--", lw=0.5, color="gray", alpha=0.4)
    ax_bar.spines["top"].set_visible(False)
    ax_line.spines["top"].set_visible(False)


def _setup_legend(ax_bar: Axes, ax_line: Axes, cfg: dict) -> None:
    """[辅助函数] 合并双轴图例"""
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


def make_plot(df: pd.DataFrame, cfg: dict):
    """绘制静态图"""
    years = df[cfg["col_year"]].values
    stock = df[cfg["col_stock"]].values * cfg["stock_factor"]
    flow = df[cfg["col_flow"]].values * cfg["flow_factor"]

    fig, ax_bar = plt.subplots(figsize=cfg["figsize"])  # type: (Figure, Axes)
    ax_line = ax_bar.twinx()  # type: Axes

    # 绘图
    bars = ax_bar.bar(
        years,
        stock,
        color=cfg["color_stock"],
        width=0.5,
        zorder=2,
        label=cfg["label_stock"],
    )
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

    # 应用统一的轴设置
    _setup_axes(ax_bar, ax_line, cfg)
    _setup_legend(ax_bar, ax_line, cfg)

    # 高亮特定年份
    for bar, year in zip(bars, years):
        if year in cfg["highlight_years"]:
            bar.set_color(cfg["highlight_color"])

    # 标题与保存
    fig.suptitle(cfg["title"])
    fig.tight_layout()

    # 确保父目录存在
    cfg["save_path"].parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(cfg["save_path"], dpi=cfg["dpi"], bbox_inches="tight")
    print(f"✅ 静态图已保存 → {cfg['save_path']}")
    plt.show()


def make_anim(df: pd.DataFrame, cfg: dict):
    """绘制生长动画"""
    years = df[cfg["col_year"]].values
    stock = df[cfg["col_stock"]].values * cfg["stock_factor"]
    flow = df[cfg["col_flow"]].values * cfg["flow_factor"]
    n = len(years)

    fig, ax_bar = plt.subplots(figsize=cfg["figsize"])
    ax_line = ax_bar.twinx()

    # 初始化空图表对象
    bars = ax_bar.bar(
        years,
        np.zeros_like(stock),  # 初始高度为0
        color=cfg["color_stock"],
        width=0.5,
        zorder=2,
        label=cfg["label_stock"],
    )
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

    # 应用统一设置
    _setup_axes(ax_bar, ax_line, cfg)
    _setup_legend(ax_bar, ax_line, cfg)

    # 预先设置高亮颜色（虽然此时高度为0，但颜色属性已附着）
    for bar, year in zip(bars, years):
        if year in cfg["highlight_years"]:
            bar.set_color(cfg["highlight_color"])

    fig.suptitle(cfg["title"])
    fig.tight_layout()

    # 动画逻辑参数
    k = cfg["k"]  # 每一年的生长步数
    slow_frames = n * k + 1

    def init():
        """初始化帧"""
        for b in bars:
            b.set_height(0)
        line_dot.set_data([], [])
        return list(bars.patches) + [line_dot]

    def grow_slow(frame):
        """帧更新函数"""
        year_idx = min(frame // k, n - 1)  # 当前生长到第几年
        step_in_year = frame % k  # 当前年在第几步

        # 计算比例：如果是过去年份，比例为1；如果是当前生长年份，计算线性插值
        ratio = step_in_year / k if frame < n * k else 1.0

        # 1. 更新柱子
        # 将当前年份之前的所有柱子设为全高
        for idx in range(year_idx):
            bars[idx].set_height(stock[idx])

        # 让当前年份的柱子生长
        if year_idx < n:
            bars[year_idx].set_height(stock[year_idx] * ratio)
            bars[year_idx].set_y(0)  # 确保底部对其

        # 2. 更新折线
        # 计算当前动态点的位置（从 base 涨到 实际值）
        flow_span = flow[year_idx] - cfg["base"]
        y_current_growing = cfg["base"] + flow_span * ratio

        # 准备X和Y数据
        if frame == 0:
            x_data, y_data = [], []
        else:
            x_data = years[: year_idx + 1]
            if ratio == 1.0:
                # 如果当前年走完了，直接取真实历史数据
                y_data = flow[: year_idx + 1]
            else:
                # 否则，历史数据 + 当前正在生长的点
                y_data = np.append(flow[:year_idx], y_current_growing)

        line_dot.set_data(x_data, y_data)

        # FuncAnimation 要求返回所有更新的 Artists
        return list(bars.patches) + [line_dot]

    anim = FuncAnimation(
        fig,
        grow_slow,
        frames=slow_frames,
        init_func=init,
        interval=cfg["interval"],
        repeat=False,
        blit=True,
    )

    # 保存视频
    save_path = cfg["save_path"].with_name(cfg["save_path"].stem + "_grow.mp4")
    try:
        anim.save(save_path, writer="ffmpeg", dpi=cfg["dpi"])
        print(f"✅ 动画已保存 → {save_path}")
    except Exception as e:
        print(f"❌ 动画保存失败 (可能是未安装ffmpeg): {e}")

    plt.show()


if __name__ == "__main__":
    # 程序入口
    data_df = load_data(CONFIG)
    make_plot(data_df, CONFIG)
    # make_anim(data_df, CONFIG) # 需要动画时取消注释
