# -*- coding: utf-8 -*-
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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
    "ylim_stock": (0, 6000),  # 左轴范围
    "ytick_stock": np.arange(0, 6100, 600),
    "ylim_flow": (0, 20),  # 右轴范围
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
    "title": "1982-2024年甘肃省GDP增长情况",
    "save_path": Path(r"D:\Desktop\figure.png"),
    "dpi": 600,
    "figsize": (10, 6.2),
    # 调试开关
    "debug": False,
}

# 全局字体设置
plt.rcParams["font.family"] = ["Times New Roman", "SimSun"]
plt.rcParams["font.size"] = 12
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.unicode_minus"] = False


def load_data(cfg: dict) -> pd.DataFrame:
    """读取并清洗数据，仅返回目标年份区间内记录。"""
    df = (
        pd.read_excel(cfg["file"], sheet_name=cfg["sheet"])
        .loc[:, [cfg["col_year"], cfg["col_stock"], cfg["col_flow"]]]
        .dropna(subset=[cfg["col_year"], cfg["col_stock"]])
    )
    df[cfg["col_year"]] = df[cfg["col_year"]].astype(int)

    mask = (df[cfg["col_year"]] >= cfg["year_start"]) & (
        df[cfg["col_year"]] <= cfg["year_end"]
    )
    result = df.loc[mask].sort_values(cfg["col_year"])

    if cfg.get("debug", False):
        print(result.head(10))

    return result


def _apply_axes_style(ax_bar, ax_line, cfg: dict) -> None:
    """应用双轴图通用坐标样式。"""
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

    ax_bar.grid(axis="y", ls="--", lw=0.5, color="gray", alpha=0.4)
    ax_bar.spines["top"].set_visible(False)
    ax_line.spines["top"].set_visible(False)


def _add_merged_legend(ax_bar, ax_line, cfg: dict) -> None:
    """合并双轴图例并统一样式。"""
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


def make_plot(df: pd.DataFrame, cfg: dict) -> None:
    """绘制并保存静态图。"""
    years = df[cfg["col_year"]].to_numpy()
    stock = df[cfg["col_stock"]].to_numpy() * cfg["stock_factor"]
    flow = df[cfg["col_flow"]].to_numpy() * cfg["flow_factor"]

    fig, ax_bar = plt.subplots(figsize=cfg["figsize"])
    ax_line = ax_bar.twinx()

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

    _apply_axes_style(ax_bar, ax_line, cfg)
    _add_merged_legend(ax_bar, ax_line, cfg)

    for bar, year in zip(bars, years):
        if year in cfg["highlight_years"]:
            bar.set_color(cfg["highlight_color"])

    fig.suptitle(cfg["title"])
    fig.tight_layout()

    cfg["save_path"].parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(cfg["save_path"], dpi=cfg["dpi"], bbox_inches="tight")
    print(f"✅ 已保存 → {cfg['save_path']}")
    plt.show()


def make_anim(df: pd.DataFrame, cfg: dict) -> None:
    """绘制并保存生长动画。"""
    years = df[cfg["col_year"]].to_numpy()
    stock = df[cfg["col_stock"]].to_numpy() * cfg["stock_factor"]
    flow = df[cfg["col_flow"]].to_numpy() * cfg["flow_factor"]
    n = len(years)

    fig, ax_bar = plt.subplots(figsize=cfg["figsize"])
    ax_line = ax_bar.twinx()

    _apply_axes_style(ax_bar, ax_line, cfg)

    bars = ax_bar.bar(
        years,
        np.zeros_like(stock),
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

    _add_merged_legend(ax_bar, ax_line, cfg)

    for bar, year in zip(bars, years):
        if year in cfg["highlight_years"]:
            bar.set_color(cfg["highlight_color"])

    fig.suptitle(cfg["title"])
    fig.tight_layout()

    k = cfg["k"]  # 一年分 k 步长出来，越大越慢
    slow_frames = n * k + 1

    def grow_slow(frame: int):
        year_idx = min(frame // k, n - 1)
        ratio = (frame % k) / k if frame < n * k else 1.0

        for idx in range(year_idx):
            bars[idx].set_height(stock[idx])

        if year_idx < n:
            bars[year_idx].set_height(stock[year_idx] * ratio)
            bars[year_idx].set_y(0)

        flow_span = flow[year_idx] - cfg["base"]
        y_now = cfg["base"] + flow_span * ratio

        x_data = years[: year_idx + 1] if frame else []
        if ratio == 1:
            y_data = flow[: year_idx + 1]
        else:
            y_data = np.append(flow[:year_idx], y_now)

        line_dot.set_data(x_data, y_data)
        return list(bars.patches) + [line_dot]

    def init():
        for b in bars:
            b.set_height(0)
        line_dot.set_data([], [])
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

    save_path = cfg["save_path"].with_name(cfg["save_path"].stem + "_grow.mp4")
    anim.save(save_path, writer="ffmpeg", dpi=cfg["dpi"])
    print(f"✅ 生长动画已保存 → {save_path}")
    plt.show()


if __name__ == "__main__":
    data = load_data(CONFIG)
    make_plot(data, CONFIG)
    # make_anim(data, CONFIG)
