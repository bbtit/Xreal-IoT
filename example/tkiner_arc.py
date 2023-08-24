import tkinter as tk
import threading
import queue
from time import sleep
import random


def move_arc():
    global current_id
    prev_id = current_id
    input_degree = q.get()
    start_degree = input_degree - 5
    arc_length = 10
    current_id = canvas.create_arc(
        upper_left[0],
        upper_left[1],
        lower_right[0],
        lower_right[1],
        start=start_degree,
        extent=arc_length,
        style=tk.ARC,
        outline="red",
        width=10,
    )
    canvas.delete(prev_id)
    canvas.after(100, move_arc)


def worker():
    while True:
        # Generate a random number between 0 and 360
        random_number = random.randint(0, 360)
        print(random_number)
        # Put the number in the queue
        q.put(random_number)

        # Sleep for 1 second
        sleep(1)


# ルートウィンドウの作成
root = tk.Tk()

# ウィンドウのサイズを画面の解像度に合わせる
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}+0+0")
root.attributes("-fullscreen", True)

# キャンバスの作成
canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg="black")
canvas.pack()

# 円の中心
circle_center = (screen_width / 2, screen_height / 2)
# 円の半径
circle_radius = min(screen_width, screen_height) / 2 - 200

# 円の左上と右下の座標
upper_left = (
    circle_center[0] - circle_radius,
    circle_center[1] - circle_radius,
)
lower_right = (
    circle_center[0] + circle_radius,
    circle_center[1] + circle_radius,
)


# ! 処理の開始
# queueを作成
q = queue.Queue()
# スレッドを作成してququeに値を入れる
t = threading.Thread(target=worker, args=())
t.start()

current_id = canvas.create_arc(
    upper_left[0],
    upper_left[1],
    lower_right[0],
    lower_right[1],
    start=0,
    extent=10,
    style=tk.ARC,
    outline="red",
    width=10,
)
root.after(1, move_arc())

# イベントループの開始
root.mainloop()
