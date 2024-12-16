import matplotlib.pyplot as plt
import numpy as np

# 数据
cores = [16, 8, 4, 2, 1]
time = [4.1, 4.9, 7.6, 12, 20]
cores_curve = np.linspace(1, 16, 100)
time_curve = 20 / cores_curve

绘图
plt.figure(figsize=(8, 6))
plt.plot(cores, time, '-o', label='test', linewidth=2)  # 实线折线
plt.plot(cores_curve, time_curve, '--', label='optimal', linewidth=2)  # 虚线曲线

# 设置图例和标签
plt.xlabel('Cores', fontsize=12)
plt.ylabel('Min', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=10)
plt.xticks(cores)
plt.tight_layout()

# 绘制柱状图（宽度改为一半）
plt.figure(figsize=(8, 6))
plt.bar(labels, time, width=0.3, edgecolor='black', alpha=0.8)

设置标签
plt.xlabel('Dataset Size', fontsize=12)
plt.ylabel('Min', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# 添加数据标签
for i, v in enumerate(time):
    plt.text(i, v + 0.1, f"{v} Min", ha='center', fontsize=10)

import matplotlib.pyplot as plt
import numpy as np

# 数据
cores = [16, 8, 4, 2, 1]
time = [4.1, 3.5, 3.3, 3.0, 2.9]

# 绘制柱状图
plt.figure(figsize=(8, 6))
plt.bar(cores, time, width=0.6, edgecolor='black', alpha=0.8)

# 设置标签
plt.xlabel('Cores', fontsize=12)
plt.ylabel('Min', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.xticks(cores)
plt.tight_layout()

# 添加数据标签
for i, v in enumerate(time):
    plt.text(cores[i], v + 0.1, f"{v} Min", ha='center', fontsize=10)

# 展示图形
plt.show()