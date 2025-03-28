import numpy as np
import matplotlib.pyplot as plt

# 数据
x = np.array([-10, -9, -8, -7,  -6,  -5, -4,  -3,   -2,   -1,   0,   1, 2,  3, 4, 5, 6,   7, 8,   9, 10])
y = np.array([  0, 0.1, 0.2, 0.3, 0.35, 0.4, 0.45, 0.5,  1,  1.2, 1.5, 1.8, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5,  6])
# y = np.array([  0,  1,  1,  1, 1.5,   2,  2, 2.5,  2.5,  2.5,   3,   3, 3,  3, 3, 4, 4, 4.5, 5, 5.5,  6])

# 二次多项式拟合
coefficients = np.polyfit(x, y, 15)
poly = np.poly1d(coefficients)
y_fit = poly(x)

v = poly(0.5)
print(v)
print(type(v))

# 计算R²
residuals = y - y_fit
ss_res = np.sum(residuals**2)
ss_tot = np.sum((y - np.mean(y))**2)
r_squared = 1 - (ss_res / ss_tot)

# 绘图
plt.scatter(x, y, label='Data')
plt.plot(x, y_fit, color='red', label=f'Fit: $R^2 = {r_squared:.3f}$')
plt.legend()
plt.show()

print("系数（高次到低次）:", coefficients)
print("R²:", r_squared)