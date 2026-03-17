# src/Work0/main.py
import taichi as ti
import inspect
# 注意：初始化必须在最前面执行，接管底层 GPU
ti.init(arch=ti.gpu)

# 导入我们自己写的模块
from .config import WINDOW_RES, PARTICLE_COLOR, PARTICLE_RADIUS
from .physics import init_particles, update_particles, pos


def _hex_to_rgb(color: int):
    return ((color >> 16 & 0xFF) / 255.0, (color >> 8 & 0xFF) / 255.0, (color & 0xFF) / 255.0)

def _create_window():
    """兼容不同 Taichi 版本的 Window 初始化参数。"""
    window_kwargs = {"res": WINDOW_RES}

    # 新版本支持 resizable，旧版本不支持。
    try:
        params = inspect.signature(ti.ui.Window).parameters
        if "resizable" in params:
            window_kwargs["resizable"] = True
    except (TypeError, ValueError):
        # 某些版本的 Window 可能无法反射签名，直接使用基础参数。
        pass

    return ti.ui.Window("Experiment 0: Taichi Gravity Swarm", **window_kwargs)
def _pixel_radius_to_canvas_radius(pixel_radius: float, width: float, height: float) -> float:
    """将像素半径换算为 GGUI circles 使用的归一化半径。"""
    base = min(width, height) if width > 0 and height > 0 else min(WINDOW_RES)
    return pixel_radius / base
def run():
    print("正在编译 GPU 内核，请稍候...")
    init_particles()

    particle_color = _hex_to_rgb(PARTICLE_COLOR)
    pos_draw = ti.Vector.field(2, dtype=ti.f32, shape=pos.shape[0])
    # 使用 GGUI 窗口，支持运行时调整大小
    window = _create_window()
    
    canvas = window.get_canvas()
    print("编译完成！请在弹出的窗口中移动鼠标。")

    # 渲染主循环
    while window.running:
        mouse_x, mouse_y = window.get_cursor_pos()
        if hasattr(window, "get_window_shape"):
            width, height = window.get_window_shape()
            #aspect = width / height if height > 0 else WINDOW_RES[0] / WINDOW_RES[1]
        else:
            # 兼容较老版本：没有动态窗口尺寸接口时退化为配置值
            #aspect = WINDOW_RES[0] / WINDOW_RES[1]
             width, height = WINDOW_RES

        aspect = width / height if height > 0 else WINDOW_RES[0] / WINDOW_RES[1]
        canvas_radius = _pixel_radius_to_canvas_radius(PARTICLE_RADIUS, width, height)

        # 驱动 GPU 进行物理计算（传入宽高比）
        update_particles(mouse_x, mouse_y, aspect)

        # 每帧从 GPU 回传到 CPU（会变慢/更不“黏”）
        pos_np = pos.to_numpy().astype("float32", copy=False)
        pos_draw.from_numpy(pos_np)

        canvas.set_background_color((0.0, 0.0, 0.0))
        canvas.circles(pos_draw, color=particle_color, radius=canvas_radius)
        window.show()


if __name__ == "__main__":
    run()
