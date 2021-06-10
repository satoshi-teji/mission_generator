from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import json
from collections import defaultdict, deque
import signal

from rospy.rostime import Duration


class MissionGenerator:
    def __init__(self, root):
        self._datalist = np.empty((0, 6), int)
        self.rowspan = 42
        self.columnspan = 20
        self.root = root

        style = ttk.Style()
        style.configure("BW.TLabel", foreground="black", background="white")

        self.root.title("Mission Generator")
        self.mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, S, E))
        self.content = Canvas(self.mainframe, borderwidth=5, relief="ridge")
        self.content.grid(column=0, row=0, columnspan=self.columnspan, rowspan=self.rowspan)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Yawに関する表示処理
        ttk.Label(self.mainframe, text="Yaw(0->N 90->E...): ").grid(column=self.columnspan + 1, row=0, sticky="E")
        ttk.Label(self.mainframe, text="deg").grid(column=self.columnspan + 3, row=0, sticky="E")
        self.yaw = StringVar()
        self.yaw.set("0")
        yaw_entry = ttk.Entry(self.mainframe, width=5, textvariable=self.yaw).grid(column=self.columnspan + 2, row=0, sticky="W")

        # margin に関する表示処理
        ttk.Label(self.mainframe, text="margin: ").grid(column=self.columnspan + 1, row=1, sticky="E")
        ttk.Label(self.mainframe, text="m").grid(column=self.columnspan + 3, row=1, sticky="E")
        self.margin = StringVar()
        self.margin.set("2.0")
        margin_entry = ttk.Entry(self.mainframe, width=5, textvariable=self.margin).grid(column=self.columnspan + 2, row=1, sticky="W")

        # duration に関する表示処理
        ttk.Label(self.mainframe, text="duration: ").grid(column=self.columnspan + 1, row=2, sticky="E")
        ttk.Label(self.mainframe, text="sec").grid(column=self.columnspan + 3, row=2, sticky="E")
        self.duration = StringVar()
        self.duration.set("216000")
        duration_entry = ttk.Entry(self.mainframe, width=10, textvariable=self.duration).grid(column=self.columnspan + 2, row=2, sticky="W")

        # timeout に関する表示処理
        ttk.Label(self.mainframe, text="timeout: ").grid(column=self.columnspan + 1, row=3, sticky="E")
        ttk.Label(self.mainframe, text="sec").grid(column=self.columnspan + 3, row=3, sticky="E")
        self.timeout = StringVar()
        self.timeout.set("216000")
        timeout_entry = ttk.Entry(self.mainframe, width=10, textvariable=self.timeout).grid(column=self.columnspan + 2, row=3, sticky="W")

        # (x, y, yaw)に関する表示処理
        ttk.Button(self.mainframe, text="Waypoints List", command=self.wpl_viewer).grid(column=self.columnspan + 1, row=4, sticky="E")

        # xlimの設定
        ttk.Label(self.mainframe, text="x range:").grid(column=0, row=43, sticky="E")
        self.x_min = StringVar()
        self.x_min.set("-50")
        x_min_entry = ttk.Entry(self.mainframe, width=5, textvariable=self.x_min).grid(column=1, row=43, sticky="W")
        ttk.Label(self.mainframe, text="< x <").grid(column=2, row=43, sticky="W")
        self.x_max = StringVar()
        self.x_max.set("50")
        x_max_entry = ttk.Entry(self.mainframe, width=5, textvariable=self.x_max).grid(column=3, row=43, sticky="W")
        self.xlim = [-50, 50]

        # ylimの設定
        ttk.Label(self.mainframe, text="y range:").grid(column=0, row=44, sticky="E")
        self.y_min = StringVar()
        self.y_min.set("-50")
        y_min_entry = ttk.Entry(self.mainframe, width=5, textvariable=self.y_min).grid(column=1, row=44, sticky="W")
        ttk.Label(self.mainframe, text="< y <").grid(column=2, row=44, sticky="W")
        self.y_max = StringVar()
        self.y_max.set("50")
        y_max_entry = ttk.Entry(self.mainframe, width=5, textvariable=self.y_max).grid(column=3, row=44, sticky="W")
        self.ylim = [-50, 50]

        # repeat
        self.n_repeat = StringVar()
        self.n_repeat.set("1")
        n_repeat_entry = ttk.Entry(self.mainframe, width=5, textvariable=self.n_repeat).grid(column=self.columnspan - 6, row=43, sticky="W")
        ttk.Button(self.mainframe, text="repeat", command=self.repeat).grid(column=self.columnspan - 5, row=43, sticky="W")

        # save
        ttk.Button(self.mainframe, text="save", command=self.to_json).grid(column=self.columnspan - 1, row=43, sticky="W")

        # clear
        ttk.Button(self.mainframe, text="clear", command=self.clear).grid(column=self.columnspan - 1, row=44, sticky="W")

        # undo
        ttk.Button(self.mainframe, text="undo", command=self.undo).grid(column=self.columnspan - 5, row=44, sticky="W")

        # add
        ttk.Label(self.mainframe, text="x y yaw:").grid(column=0, row=45, sticky="E")
        self.x = StringVar()
        self.x.set("x")
        x_entry = ttk.Entry(self.mainframe, width=5, textvariable=self.x).grid(column=1, row=45, sticky="W")
        self.y = StringVar()
        self.y.set("y")
        y_entry = ttk.Entry(self.mainframe, width=5, textvariable=self.y).grid(column=2, row=45, sticky="W")
        self._yaw = StringVar()
        self._yaw.set("yaw")
        yaw_entry = ttk.Entry(self.mainframe, width=5, textvariable=self._yaw).grid(column=3, row=45, sticky="W")
        ttk.Button(self.mainframe, text="add waypoint", command=self.add_waypoint).grid(column=4, row=45, sticky="W")

        # グラフの準備
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.set_xlim(-50, 50)
        self.ax.set_ylim(-50, 50)
        self.ax.set_xlabel("Y[m]")
        self.ax.set_ylabel("X[m]")
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.content)
        self.canvas.get_tk_widget().grid(column=0, row=0, sticky="NWES")
        self.canvas.mpl_connect("button_press_event", self.onclick)

        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=1, pady=1)

        # lim自動適用
        self.update_lims(self.root)

        # Windowを閉じたときの処理
        self.root.protocol("WM_DELETE_WINDOW", self._destroyWindow)
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def onclick(self, event):
        try:
            x, y, yaw, margin, duration, timeout = (
                np.round(event.xdata),
                np.round(event.ydata),
                float(self.yaw.get()),
                float(self.margin.get()),
                float(self.duration.get()),
                float(self.timeout.get()),
            )
        except (ValueError, TypeError):
            return
        if (x == None) or (y == None):
            return
        button = int(event.button)
        if button == 1:  # Left click: add waypoint
            try:
                y_, x_, yaw_, _, _, _ = self._datalist[-1, :]
                if (x == x_) and (y == y_) and (yaw_ == float(yaw)):
                    return
            except IndexError:
                pass
            self._datalist = np.append(self._datalist, np.array([[y, x, yaw, margin, duration, timeout]]), axis=0)
            self.ax.plot(self._datalist[:, 1], self._datalist[:, 0], ".", color="red")
            self.draw_arrows(self._datalist.shape[0] - 1)
        elif button == 3:  # Right click: remove waypoint
            diff = self._datalist - np.array([y, x, yaw, margin, duration, timeout]).T
            diff = np.linalg.norm(diff, axis=1)
            if diff.min() <= 2:
                index = diff.argmin()
                self._datalist = np.delete(self._datalist, index, axis=0)
            else:
                return
            self.redraw()

    # waypointにどの順番で向かうかを可視化する
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

    def redraw(self):
        self.ax.cla()
        self.ax.set_ylim(int(self.x_min.get()), int(self.x_max.get()))
        self.ax.set_xlim(int(self.y_min.get()), int(self.y_max.get()))
        self.ax.set_xlabel("Y[m]")
        self.ax.set_ylabel("X[m]")
        self.ax.grid(True)
        self.ax.plot(self._datalist[:, 1], self._datalist[:, 0], ".", color="red")
        for i in range(1, self._datalist.shape[0]):
            self.draw_arrows(i)
        self.canvas.draw_idle()

    def update_lims(self, *args):
        self.change_x_range(), self.change_y_range()
        self.root.after(500, self.update_lims)

    def change_x_range(self, *args):
        try:
            x_min, x_max = int(self.x_min.get()), int(self.x_max.get())
            if self.xlim == [x_min, x_max]:
                return
            self.xlim = [x_min, x_max]
            self.ax.set_ylim(x_min, x_max)
            self.canvas.draw_idle()
        except ValueError:
            pass

    def change_y_range(self, *args):
        try:
            y_min, y_max = int(self.y_min.get()), int(self.y_max.get())
            if self.ylim == [y_min, y_max]:
                return
            self.ylim = [y_min, y_max]
            self.ax.set_xlim(y_min, y_max)
            self.canvas.draw_idle()
        except ValueError:
            pass

    def clear(self, *args):
        self.ax.cla()
        self.ax.set_xlim(-50, 50)
        self.ax.set_ylim(-50, 50)
        self.ax.set_xlabel("Y[m]")
        self.ax.set_ylabel("X[m]")
        self.ax.grid(True)
        self.canvas.draw_idle()
        self._datalist = np.empty((0, 6), int)
        messagebox.showinfo("Clear info", "Done!")

    def repeat(self, *args):
        try:
            margin, duration, timeout = (
                float(self.margin.get()),
                float(self.duration.get()),
                float(self.timeout.get()),
            )
            n = int(self.n_repeat.get())
            data = self._datalist
            if self._datalist.shape[0]:
                for _ in range(n):
                    for i in range(1, data.shape[0]):
                        diffs = data[i, :] - data[i - 1, :]
                        yaw = data[i, 2]
                        y, x, _, _, _, _ = diffs + self._datalist[-1, :]
                        self._datalist = np.append(self._datalist, np.array([[y, x, yaw, margin, duration, timeout]]), axis=0)
                self.redraw()
                messagebox.showinfo("Repeat info", "Done!")
            else:
                messagebox.showerror("Error!", "No waypoints are selected")
        except ValueError:
            messagebox.showerror("Error!", "ValueError: repeat num is invalid")
            return

    def undo(self, *args):
        try:
            self._datalist = np.delete(self._datalist, -1, axis=0)
            self.redraw()
        except IndexError:
            pass

    def add_waypoint(self, *args):
        try:
            x, y, yaw, margin, duration, timeout = (
                float(self.x.get()),
                float(self.y.get()),
                float(self._yaw.get()),
                float(self.margin.get()),
                float(self.duration.get()),
                float(self.timeout.get()),
            )
            self._datalist = np.append(self._datalist, np.array([[y, x, yaw, margin, duration, timeout]]), axis=0)
            self.redraw()
        except ValueError:
            pass

    def to_json(self, *args):
        data = defaultdict(list)
        if not self._datalist.shape[0]:
            messagebox.showerror("Error!", "No waypoints are selected")
            return
        for i, xyymdt in enumerate(self._datalist):
            x, y, yaw, margin, duration, timeout = xyymdt
            d = {"ID": i, "X": x, "Y": y, "Yaw": yaw, "Margin": margin, "Duration": duration, "Timeout": timeout}
            data["waypoints"].append(d)
        with open("./mission.json", mode="wt", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        messagebox.showinfo("Save info", "Done!")

    def wpl_viewer(self, *args):
        newWindow = Toplevel(self.root)
        message = ScrolledText(newWindow, width=90, height=30)
        message.pack()
        if self._datalist.size > 0:
            for i, xyy in enumerate(self._datalist):
                m = "{0}: x:{1} y:{2} yaw:{3} margin:{4} duration:{5} timeout:{6}\n".format(i + 1, *xyy)
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
    root = Tk()
    MissionGenerator(root)
    root.mainloop()
