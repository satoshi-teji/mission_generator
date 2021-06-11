import json
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import signal

import rospy


class MissionVisualizer:
    def __init__(self, root):
        self._datalist = np.empty((0, 6), int)
        self.rowspan = 1
        self.columnspan = 2
        self.root = root
        self.x_min = 10 ** 9
        self.x_max = -(10 ** 9)
        self.y_min = 10 ** 9
        self.y_max = -(10 ** 9)

        self.filename = "mission.json"  # rospy

        # tkinter
        style = ttk.Style()
        style.configure("BW.TLabel", foreground="black", background="white")

        self.root.title("Mission Visualizer")
        self.mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, S, E))
        self.content = Canvas(self.mainframe, borderwidth=5, relief="ridge")
        self.content.grid(
            column=0, row=0, columnspan=self.columnspan, rowspan=self.rowspan
        )
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # グラフの準備
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.set_xlim(-50, 50)
        self.ax.set_ylim(-50, 50)
        self.ax.set_xlabel("Y[m]")
        self.ax.set_ylabel("X[m]")
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.content)
        self.canvas.get_tk_widget().grid(column=0, row=0, sticky="NWES")

        # json読み込み
        self.from_json(filename=self.filename)
        self.draw()

        # waypoints listの表示
        ttk.Button(self.mainframe, text="Waypoints List", command=self.wpl_viewer).grid(
            column=0, row=1, sticky="E"
        )
        # Windowを閉じたときの処理
        self.root.protocol("WM_DELETE_WINDOW", self._destroyWindow)

    def from_json(self, filename):
        with open(filename, mode="r") as f:
            data = json.load(f)
        wpl = data["waypoints"]

        for wp in wpl:
            _, x, y, yaw, margin, duration, timeout = wp.values()
            self.x_min = min(self.x_min, y)
            self.x_max = max(self.x_max, y)
            self.y_min = min(self.y_min, x)
            self.y_max = max(self.y_max, x)
            self._datalist = np.append(
                self._datalist, np.array([[y, x, yaw, margin, duration, timeout]]), axis=0
            )

    def draw(self):
        self.ax.cla()
        # いい感じに表示する
        self.ax.set_ylim(
            int(self.x_min - self.x_min % 10 - 10), int(self.x_max - self.x_max % 10 + 10)
        )
        self.ax.set_xlim(
            int(self.y_min - self.y_min % 10 - 10), int(self.y_max - self.y_max % 10 + 10)
        )
        self.ax.set_xlabel("Y[m]")
        self.ax.set_ylabel("X[m]")
        self.ax.grid(True)
        self.ax.plot(self._datalist[:, 1], self._datalist[:, 0], ".", color="red")
        for i in range(1, self._datalist.shape[0]):
            self.draw_arrows(i)
        self.canvas.draw_idle()

    def draw_arrows(self, n):
        start = self._datalist[n - 1, :]
        end = self._datalist[n, :]
        start = np.array([start[1], start[0]])
        end = np.array([end[1], end[0]])
        self.ax.annotate(
            "",
            xy=end,
            xytext=start,
            arrowprops=dict(
                shrink=0,
                width=1,
                headwidth=8,
                headlength=10,
                connectionstyle="arc3",
                facecolor="black",
                edgecolor="black",
            ),
        )
        self.canvas.draw_idle()

    def wpl_viewer(self, *args):
        newWindow = Toplevel(self.root)
        message = ScrolledText(newWindow, width=90, height=30)
        message.pack()
        if self._datalist.size > 0:
            for i, xyy in enumerate(self._datalist):
                m = "{0}: x:{1} y:{2} yaw:{3} margin:{4} duration:{5} timeout:{6}\n".format(
                    i + 1, *xyy
                )
                message.insert(float(i + 1), m)
        else:
            message.insert(1.0, "No waypoints")
        message.configure(state="disabled")
        newWindow.title("Waypoints List")
        newWindow.geometry("800x300")
        newWindow.grab_set()
        self.root.wait_window(newWindow)
        newWindow.destroy()

    def _destroyWindow(self):
        self.root.quit()
        self.root.destroy()


if __name__ == "__main__":
    app = Tk()
    MissionVisualizer(app)
    app.mainloop()
