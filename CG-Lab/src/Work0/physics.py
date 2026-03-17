# src/Work0/physics.py
import taichi as ti
from .config import *

# 1. 数据结构定义：在显存中开辟空间
pos = ti.Vector.field(2, dtype=float, shape=NUM_PARTICLES)
vel = ti.Vector.field(2, dtype=float, shape=NUM_PARTICLES)


@ti.kernel
def init_particles():
    """初始化每一个粒子的随机坐标"""
    for i in range(NUM_PARTICLES):
        pos[i] = [ti.random(), ti.random()]
        vel[i] = [0.0, 0.0]


@ti.kernel
def update_particles(mouse_x: float, mouse_y: float, aspect: float):
    """物理更新：由 GPU 并行执行。aspect 用于屏幕宽高比补偿。"""
    for i in range(NUM_PARTICLES):
        # 计算方向与距离（先做屏幕空间补偿）
        d = ti.Vector([mouse_x - pos[i].x, mouse_y - pos[i].y])
        d.x *= aspect
        dist = d.norm()

        # 施加引力与阻力
        if dist > 0.05:
            accel = d.normalized() * GRAVITY_STRENGTH
            # 还原到归一化坐标空间
            accel.x /= aspect
            vel[i] += (accel/120)

        vel[i] *= DRAG_COEF
        pos[i] += vel[i]

        # 边框碰撞检测
        for j in ti.static(range(2)):
            if pos[i][j] < 0:
                pos[i][j] = 0.0
                vel[i][j] *= BOUNCE_COEF
            elif pos[i][j] > 1:
                pos[i][j] = 1.0
                vel[i][j] *= BOUNCE_COEF
