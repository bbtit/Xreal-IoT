import tkinter as tk
from queue import Queue


class WindowCanvasManager:
    def __init__(self, bg_color="black"):
        # ルートウィンドウの作成
        self.root = tk.Tk()

        # ウィンドウのサイズを画面の解像度に合わせる
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.attributes("-fullscreen", True)

        # 円の中心
        self.circle_center = (screen_width / 2, screen_height / 2)
        # 円の半径
        self.circle_radius = min(screen_width, screen_height) / 2 - 200

        # 円の左上と右下の座標
        self.upper_left = (
            self.circle_center[0] - self.circle_radius,
            self.circle_center[1] - self.circle_radius,
        )
        self.lower_right = (
            self.circle_center[0] + self.circle_radius,
            self.circle_center[1] + self.circle_radius,
        )

        # キャンバスの作成
        self.canvas = tk.Canvas(
            self.root, width=screen_width, height=screen_height, bg=bg_color
        )
        self.canvas.pack()

        # 描写された図形とテキストのIDを保持
        self.drown_arc_id = None
        self.drown_text_id = None

    def create_arc(self, *args, **kwargs):
        self.drown_arc_id = self.canvas.create_arc(*args, **kwargs)
        return self.drown_arc_id

    def create_text(self, *args, **kwargs):
        self.drawn_text_id = self.canvas.create_text(*args, **kwargs)
        return self.drawn_text_id

    def update_arc_angle(self, obj_id, start_angle):
        # 指定されたIDの円弧の角度を変更する
        self.canvas.itemconfig(obj_id, start=start_angle)

    def update_text_content(self, obj_id, new_text):
        # 指定されたIDのテキストオブジェクトの内容を新しいテキストで更新する
        self.canvas.itemconfig(obj_id, text=new_text)

    def delete_object(self, obj_id):
        self.canvas.delete(obj_id)

    def draw_voice_angle_arc_forever(self, queue: Queue):
        # Queueから角度を取得し、円弧を描画する
        input_degree: int = queue.get_nowait() if not queue.empty() else None

        if input_degree is None:
            # 再帰呼び出し
            self.root.after(1000, self.draw_voice_angle_arc_forever, queue)
            return

        # 今まで円弧が描画されていない場合は描画する
        if self.drown_arc_id is None:
            self.create_arc(
                self.upper_left[0],
                self.upper_left[1],
                self.lower_right[0],
                self.lower_right[1],
                start=0,
                extent=10,
                style=tk.ARC,
                outline="red",
                width=10,
            )
            # 再帰呼び出し
            self.root.after(1000, self.draw_voice_angle_arc_forever, queue)
            return

        # 円弧の角度を変更
        self.update_arc_angle(self.drown_arc_id, input_degree - 5)
        # 再帰呼び出し
        self.root.after(1000, self.draw_voice_angle_arc_forever, queue)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    import random
    import threading
    from time import sleep

    def worker(q: Queue):
        while True:
            # Generate a random number between 0 and 360
            random_number = random.randint(0, 360)
            print(random_number)
            # Put the number in the queue
            q.put(random_number)

            # Sleep for 1 second
            sleep(1)

    q = Queue()
    t = threading.Thread(target=worker, args=(q,))
    t.start()

    window_canvas = WindowCanvasManager()
    window_canvas.draw_voice_angle_arc_forever(q)
    window_canvas.run()
