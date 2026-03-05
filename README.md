# CG-Lab Homework 1：Taichi 粒子引力实验

本项目是一个基于 **Taichi + GPU 并行计算** 的图形学小实验：
- 在窗口中实时模拟大量粒子运动；
- 鼠标位置作为“引力源”吸引粒子；
- 粒子具有阻力衰减与边界反弹效果。

---

## 1. 项目架构

```text
README.md                   # 项目说明文档
CG-Lab/
├── pyproject.toml          # 项目依赖与 Python 版本要求
├── Video Project.mp4       # 项目演示视频
└── src/
    └── Work0/
        ├── __init__.py       
        ├── main.py         # 程序入口：GUI 循环 + 调度物理更新
        ├── config.py       # 参数配置：粒子数量、阻力、窗口尺寸等
        └── physics.py      # 核心物理计算内核（Taichi kernel）
```

模块职责：
- `config.py`：集中配置物理参数与渲染参数，便于快速调参。
- `physics.py`：定义 `pos/vel` 场并在 GPU 上并行更新。
- `main.py`：初始化 Taichi、读取鼠标输入、调用 kernel、绘制粒子。

---

## 2. 代码逻辑（运行流程）

### 2.1 启动阶段
1. `ti.init(arch=ti.gpu)` 初始化 Taichi，启用 GPU 后端。
2. `init_particles()` 在 `[0,1] x [0,1]` 范围随机生成粒子初始位置，并把速度置零。
3. 创建 `ti.GUI` 窗口。

### 2.2 每帧更新阶段
主循环中每帧执行：
1. 读取鼠标坐标 `(mouse_x, mouse_y)`。
2. 调用 `update_particles(mouse_x, mouse_y)`：
   - 计算粒子到鼠标的方向和距离；
   - 距离大于阈值时施加引力加速度；
   - 应用空气阻力（速度衰减）；
   - 更新位置；
   - 做边界碰撞检测并按系数反弹。
3. 将 `pos` 从显存读取后用 `gui.circles(...)` 批量绘制。

---

## 3. 已实现功能

-  **万级粒子实时仿真**（默认 10000 个）。
-  **鼠标交互引力**：鼠标移动可实时改变粒子流向。
-  **边界碰撞与能量损耗**：撞墙反弹并衰减速度。
-  **可配置参数系统**：可在 `config.py` 中直接调整核心效果。

---

## 4. 参数说明（`src/Work0/config.py`）

- `NUM_PARTICLES`：粒子总数。
- `GRAVITY_STRENGTH`：鼠标引力强度。
- `DRAG_COEF`：空气阻力系数。
- `BOUNCE_COEF`：边界反弹系数（含能量损失）。
- `WINDOW_RES` / `PARTICLE_RADIUS` / `PARTICLE_COLOR`：渲染参数。

> 如果运行卡顿，优先降低 `NUM_PARTICLES`（例如从 10000 调到 2000）。

---

## 5. 运行方式

推荐使用 `uv` 进行项目级环境管理（会在项目内自动创建 `.venv/`，避免全局环境污染）。

### 5.1 初始化与安装依赖

在 `CG-Lab/` 根目录下执行：

```bash
# 初始化项目（首次使用时执行，可指定 Python 版本）
uv init --python 3.12

# 同步依赖并创建 .venv
uv sync

# 安装 Taichi
uv add taichi
```

可用 `uv tree` 查看当前依赖树。

### 5.2 使用 src 布局运行

采用 `src` 布局后，务必保证终端当前路径在 `CG-Lab/` 根目录（不要进入 `src/` 再运行）。

```bash
# 使用模块模式运行（推荐）
uv run -m src.Work0.main
```

`-m` 模式会让 Python 正确按包路径解析模块，能有效避免相对导入导致的 `ModuleNotFoundError` 问题。

运行后移动鼠标，即可观察粒子群被吸引、拖尾和碰撞反弹的动态效果。

---

## 6. 演示素材（视频）

仓库中已包含演示视频，可直接查看：

- [项目演示视频（MP4）](../Video%20Project.mp4)
