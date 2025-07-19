#!/usr/bin/env python3
"""
train_gui.py  —— 图形化训练程序
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import pickle, numpy as np
from sklearn.linear_model import LinearRegression

MODEL_FILE = 'color_model.pkl'

# ---------- 小工具 ----------
def hex2rgb(h):
    h = h.lstrip('#')
    if len(h) != 6:
        raise ValueError('格式错误')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb2hex(r, g, b):
    return f'#{r:02X}{g:02X}{b:02X}'

def set_status(text, ok=True):
    var_status.set(text)
    lbl_status.config(fg='green' if ok else 'red')

def browse_actual():
    path = filedialog.askopenfilename(title='选择色差实际文件',
                                      filetypes=[('Text files', '*.txt')])
    if path:
        var_actual.set(path)

def browse_input():
    path = filedialog.askopenfilename(title='选择输入原色文件',
                                      filetypes=[('Text files', '*.txt')])
    if path:
        var_input.set(path)

def load_hex_file(path):
    with open(path, encoding='utf-8') as f:
        tokens = f.read().split()
    return [hex2rgb(t) for t in tokens if t]

def train():
    actual_path = var_actual.get()
    input_path  = var_input.get()
    if not actual_path or not input_path:
        set_status('请选择两个训练文件', ok=False)
        return

    try:
        y = load_hex_file(actual_path)  # 真实颜色
        X = load_hex_file(input_path)   # 输入色号
    except ValueError as e:
        set_status(f'颜色格式错误: {e}', ok=False)
        return

    if len(X) != len(y):
        set_status('两个文件颜色数量不一致', ok=False)
        return
    if len(X) < 3:
        set_status('至少需要 3 组数据', ok=False)
        return

    set_status('训练中...')
    root.update_idletasks()

    model = LinearRegression().fit(np.array(X), np.array(y))
    with open(MODEL_FILE, 'wb') as f:
        pickle.dump(model, f)

    set_status(f'训练完成，已保存 {MODEL_FILE}', ok=True)

# ---------------- GUI ----------------
root = tk.Tk()
root.title('模型训练')
root.resizable(False, False)

# 色差实际
tk.Label(root, text='色差实际：').grid(row=0, column=0, sticky='w', padx=10, pady=6)
var_actual = tk.StringVar()
tk.Entry(root, textvariable=var_actual, width=35).grid(row=0, column=1, padx=5)
tk.Button(root, text='浏览...', command=browse_actual).grid(row=0, column=2, padx=5)

# 输入原色
tk.Label(root, text='输入原色：').grid(row=1, column=0, sticky='w', padx=10, pady=6)
var_input = tk.StringVar()
tk.Entry(root, textvariable=var_input, width=35).grid(row=1, column=1, padx=5)
tk.Button(root, text='浏览...', command=browse_input).grid(row=1, column=2, padx=5)

# 开始训练按钮
tk.Button(root, text='开始训练', width=15, command=train)\
    .grid(row=2, column=0, columnspan=3, pady=10)

# 状态栏
var_status = tk.StringVar(value='就绪')
lbl_status = tk.Label(root, textvariable=var_status, fg='green')
lbl_status.grid(row=3, column=0, columnspan=3, pady=8)

root.mainloop()