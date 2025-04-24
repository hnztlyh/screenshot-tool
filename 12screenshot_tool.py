import os
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from PIL import ImageGrab
import threading
import subprocess
import keyboard

# 默认保存路径
save_folder = r"F:\截图"
os.makedirs(save_folder, exist_ok=True)
region = None
screenshot_count = 1
image_format = ".png"  # 默认保存格式

# 获取下一个文件名
def get_next_filename():
    global screenshot_count
    while True:
        filename = os.path.join(save_folder, f"{screenshot_count:03}{image_format}")
        if not os.path.exists(filename):
            return filename
        screenshot_count += 1

# 截图函数
def take_screenshot():
    global region, screenshot_count
    if region is None:
        messagebox.showinfo("截图", "请先选择截图区域")
        region = select_region()

    filename = os.path.join(save_folder, f"{screenshot_count:03}{image_format}")
    if os.path.exists(filename):
        overwrite = messagebox.askyesno("文件已存在", f"{filename} 已存在，是否覆盖？")
        if not overwrite:
            screenshot_count += 1
            return

    img = ImageGrab.grab(bbox=(region[0], region[1], region[0]+region[2], region[1]+region[3]))
    img.save(filename)
    status_var.set(f"已保存: {filename}")
    screenshot_count += 1

# 快捷键监听线程
def start_hotkey_listener():
    keyboard.add_hotkey('F2', lambda: threading.Thread(target=take_screenshot).start())

# 打开文件夹
def open_folder():
    try:
        subprocess.Popen(f'explorer "{save_folder}"')
    except Exception as e:
        messagebox.showerror("错误", f"无法打开文件夹: {e}")

# 设置自定义保存路径
def choose_folder():
    global save_folder
    path = filedialog.askdirectory()
    if path:
        save_folder = path
        os.makedirs(save_folder, exist_ok=True)
        status_var.set(f"保存路径已更改: {save_folder}")

# 手动输入区域
def input_region():
    global region
    try:
        import pygetwindow as gw
        import time

        w = int(simpledialog.askstring("输入", "截图宽度："))
        h = int(simpledialog.askstring("输入", "截图高度："))

        win = gw.getActiveWindow()
        if not win:
            messagebox.showerror("错误", "未能获取当前窗口信息")
            return

        try:
            win.activate()
        except:
            pass

        time.sleep(0.3)
        x, y = win.left, win.top
        region = (x, y, w, h)
        status_var.set(f"区域设置成功：窗口起点 x={x}, y={y}, w={w}, h={h}")
    except Exception as e:
        messagebox.showerror("错误", f"设置失败: {e}")

# 鼠标选择区域
def select_region():
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.attributes('-alpha', 0.3)
    root.configure(background='black')
    start_x = start_y = end_x = end_y = 0
    rect = None
    label = tk.Label(root, fg='white', bg='black', font=("宋体", 12))
    label.pack()

    def on_mouse_down(event):
        nonlocal start_x, start_y
        start_x, start_y = event.x, event.y

    def on_mouse_move(event):
        nonlocal rect
        if rect:
            canvas.delete(rect)
        rect = canvas.create_rectangle(start_x, start_y, event.x, event.y, outline='green', width=2)
        label.config(text=f"x={min(start_x, event.x)}, y={min(start_y, event.y)}, w={abs(event.x-start_x)}, h={abs(event.y-start_y)}")

    def on_mouse_up(event):
        nonlocal end_x, end_y
        end_x, end_y = event.x, event.y
        root.quit()

    canvas = tk.Canvas(root, cursor="cross")
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_move)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)
    root.mainloop()
    root.destroy()
    return (min(start_x, end_x), min(start_y, end_y), abs(end_x - start_x), abs(end_y - start_y))

# 复位并清空截图
def reset_and_clear():
    global screenshot_count
    confirm = messagebox.askyesno("确认复位", "是否清空截图文件夹，并从001重新开始？")
    if confirm:
        try:
            for f in os.listdir(save_folder):
                if f.lower().endswith(('.png', '.jpg')):
                    os.remove(os.path.join(save_folder, f))
            screenshot_count = 1
            status_var.set("截图已清空，编号已重置为001。")
        except Exception as e:
            messagebox.showerror("错误", f"清空失败: {str(e)}")

# 仅复位编号
def reset_only_number():
    global screenshot_count
    confirm = messagebox.askyesno("确认复位", "是否将截图编号重置为001？已有截图可能会被覆盖。")
    if confirm:
        screenshot_count = 1
        status_var.set("编号已重置为001，截图文件未清除。")

# 设置截图格式
def set_format(val):
    global image_format
    image_format = val
    status_var.set(f"保存格式更改为: {image_format}")

# 主界面
def start_gui():
    def on_screenshot_click():
        threading.Thread(target=take_screenshot).start()

    root = tk.Tk()
    root.title("定点截图工具")
    root.geometry("400x420")
    root.resizable(False, False)

    font_style = ("宋体", 12)


    tk.Button(root, text="📸 截图 (或按 F2)", font=font_style, command=on_screenshot_click).pack(pady=5)
    tk.Button(root, text="🔁 重新选择区域", font=font_style, command=lambda: set_region(select_region())).pack(pady=5)
    tk.Button(root, text="📝 手动输入截图区域", font=font_style, command=input_region).pack(pady=5)
    tk.Button(root, text="📂 打开截图文件夹", font=font_style, command=open_folder).pack(pady=5)
    tk.Button(root, text="📁 自定义保存路径", font=font_style, command=choose_folder).pack(pady=5)

    # 文件格式选择下拉框
    tk.Label(root, text="选择保存格式：", font=font_style).pack(pady=(10, 0))
    format_var = tk.StringVar(value=".png")
    format_menu = tk.OptionMenu(root, format_var, ".png", ".jpg", command=set_format)
    format_menu.config(font=font_style)
    format_menu.pack(pady=5)

    tk.Button(root, text="🧹 复位截图编号（清空截图）", font=font_style, command=reset_and_clear).pack(pady=5)
    tk.Button(root, text="🔢 复位截图编号（保留截图）", font=font_style, command=reset_only_number).pack(pady=5)

    global status_var
    status_var = tk.StringVar()
    status_var.set(f"保存路径: {save_folder}")
    tk.Label(root, textvariable=status_var, wraplength=350, font=font_style).pack(pady=10)

    threading.Thread(target=start_hotkey_listener, daemon=True).start()

    root.mainloop()

def set_region(r):
    global region
    region = r
    status_var.set(f"已重新设定区域: x={region[0]}, y={region[1]}, w={region[2]}, h={region[3]}")

if __name__ == "__main__":
    start_gui()
