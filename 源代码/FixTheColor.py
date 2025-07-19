#!/usr/bin/env python3
"""
FixTheColor_img_rand_guide.py
• 导入图像 → 窗口内拾色
• 预测 & 随机近似换色
• 使用指南弹窗
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import pickle, numpy as np, os, pyperclip, random
from PIL import Image, ImageTk

MODEL_FILE = 'color_model.pkl'
MAX_W, MAX_H = 400, 300     # 显示最大尺寸
DELTA = 8                   # 随机偏移 ±8

# ---------- 工具 ----------
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

# ---------- 图像画布 ----------
class ImageCanvas(tk.Canvas):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.bind("<Button-1>", self.pick_color)
        self.photo = None
        self.pil_img = None

    def load_image(self, path):
        self.pil_img = Image.open(path)
        self.pil_img.thumbnail((MAX_W, MAX_H), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(self.pil_img)
        self.config(width=self.pil_img.width, height=self.pil_img.height)
        self.create_image(0, 0, anchor='nw', image=self.photo)

    def pick_color(self, event):
        if self.pil_img is None:
            return
        scale_x = self.pil_img.width / self.winfo_width()
        scale_y = self.pil_img.height / self.winfo_height()
        px = int(event.x * scale_x)
        py = int(event.y * scale_y)
        r, g, b = self.pil_img.getpixel((px, py))
        hex_color = rgb2hex(r, g, b)
        var_target.set(hex_color)
        set_status(f'已拾取 {hex_color}', ok=True)

# ---------- 预测 ----------
def predict():
    try:
        if not os.path.exists(MODEL_FILE):
            raise FileNotFoundError('模型缺失')
        hex_str = var_target.get().strip()
        if not hex_str:
            raise ValueError('空输入')
        target_rgb = hex2rgb(hex_str)

        with open(MODEL_FILE, 'rb') as f:
            model = pickle.load(f)
        A, b = model.coef_, model.intercept_
        input_rgb = np.linalg.solve(A, np.array(target_rgb) - b)
        input_rgb = np.clip(np.round(input_rgb), 0, 255).astype(int)
        result_hex = rgb2hex(*input_rgb)

        var_result.set(result_hex)
        set_status('预测成功', ok=True)
    except Exception as e:
        set_status(str(e), ok=False)

# ---------- 随机近似换色 ----------
def random_near_color():
    base_hex = var_result.get().strip()
    if not base_hex:
        set_status('暂无结果，先预测后再换色', ok=False)
        return
    try:
        r, g, b = hex2rgb(base_hex)
        new_r = max(0, min(255, r + random.randint(-DELTA, DELTA)))
        new_g = max(0, min(255, g + random.randint(-DELTA, DELTA)))
        new_b = max(0, min(255, b + random.randint(-DELTA, DELTA)))
        new_hex = rgb2hex(new_r, new_g, new_b)
        var_result.set(new_hex)
        set_status(f'已生成近似色 {new_hex}', ok=True)
    except Exception as e:
        set_status(str(e), ok=False)

# ---------- 复制 ----------
def copy_result():
    res = var_result.get()
    if res:
        pyperclip.copy(res)
        messagebox.showinfo('提示', '已复制到剪贴板')

# ---------- 使用指南 ----------
def show_guide():
    guide_path = os.path.join(os.path.dirname(__file__), 'guide.txt')
    try:
        with open(guide_path, encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        text = '未找到 guide.txt，请确保文件存在于脚本同级目录。'

    top = tk.Toplevel(root)
    top.title('使用指南')
    top.resizable(False, False)
    txt = tk.Text(top, wrap='word', width=60, height=15)
    txt.pack(padx=10, pady=10)
    txt.insert('1.0', text)
    txt.config(state='disabled')

# ---------- GUI ----------
root = tk.Tk()
root.title('FixTheColor')
root.resizable(False, False)

# 目标颜色
tk.Label(root, text='目标真实颜色：').grid(row=0, column=0, sticky='w', padx=10, pady=6)
var_target = tk.StringVar()
tk.Entry(root, textvariable=var_target, width=12, font=('Consolas', 12))\
    .grid(row=0, column=1, padx=5)

# 按钮区
btn_frame = tk.Frame(root)
btn_frame.grid(row=1, column=0, columnspan=3, pady=6)
tk.Button(btn_frame, text='导入图像', width=10, command=lambda: canvas.load_image(
    filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.bmp")])))\
    .pack(side='left', padx=5)
tk.Button(btn_frame, text='预测', width=10, command=predict).pack(side='left', padx=5)
tk.Button(btn_frame, text='随机近似换色', width=15, command=random_near_color)\
    .pack(side='left', padx=5)
tk.Button(btn_frame, text='复制结果', width=10, command=copy_result).pack(side='left', padx=5)

# 图像画布
canvas = ImageCanvas(root, relief='solid', bd=1)
canvas.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# 结果
tk.Label(root, text='应输入色号：').grid(row=3, column=0, sticky='w', padx=10, pady=6)
var_result = tk.StringVar()
tk.Entry(root, textvariable=var_result, width=12, font=('Consolas', 12), state='readonly')\
    .grid(row=3, column=1, columnspan=2, padx=5, sticky='w')

# 状态栏
tk.Label(root, text='运行状态：').grid(row=4, column=0, sticky='w', padx=10, pady=6)
var_status = tk.StringVar(value='就绪')
lbl_status = tk.Label(root, textvariable=var_status, fg='green', font=('Consolas', 11))
lbl_status.grid(row=4, column=1, columnspan=2, sticky='w', padx=5, pady=6)

# 使用指南按钮
tk.Button(root, text='使用指南', width=12, command=show_guide)\
    .grid(row=5, column=0, columnspan=3, pady=8)

root.mainloop()