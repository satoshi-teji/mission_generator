from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import json
from collections import defaultdict


class MissionGenerator:

    def __init__(self, root):
        self._xyz = np.empty((0,3), int)
        self.rowspan = 42
        self.columnspan = 20

        style = ttk.Style()
        style.configure("BW.TLabel", foreground="black", background="white")

        root.title("Mission Generator")

        self.mainframe = ttk.Frame(root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, S, E))
        self.content = ttk.Frame(self.mainframe, borderwidth=5, relief="ridge")
        self.content.grid(column=0, row=0, columnspan=self.columnspan, rowspan=self.rowspan)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Zに関する表示処理
        ttk.Label(self.mainframe, text="Z: ").grid(column=self.columnspan + 1, row=0, sticky="E")
        self.z = StringVar()
        self.z.set("15")
        z_entry = ttk.Entry(self.mainframe, width=3, textvariable=self.z).grid(column=self.columnspan + 2, row=0, sticky="W")
        
        # (x, y, z)に関する表示処理
        self.xyz_lbls = []
        ttk.Label(self.mainframe, text="(x, y, z)").grid(column=self.columnspan + 1, row=1, sticky="E")

        # xlimの設定
        ttk.Label(self.mainframe, text="x range:").grid(column=0, row=43, sticky="E")
        self.x_min = StringVar()
        self.x_min.set("-50")
        x_min_entry = ttk.Entry(self.mainframe, width=5, textvariable=self.x_min).grid(column=1, row=43, sticky="W")
        ttk.Label(self.mainframe, text="< x <").grid(column=2, row=43, sticky="W")
        self.x_max = StringVar()
        self.x_max.set("50")
        x_max_entry = ttk.Entry(self.mainframe, width=5, textvariable=self.x_max).grid(column=3, row=43, sticky="W")
        ttk.Button(self.mainframe, text="apply", command=self.change_x_range).grid(column=4, row=43, sticky="W")

        # ylimの設定
        ttk.Label(self.mainframe, text="y range:").grid(column=0, row=44, sticky="E")
        self.y_min = StringVar()
        self.y_min.set("-50")
        y_min_entry = ttk.Entry(self.mainframe, width=5, textvariable=self.y_min).grid(column=1, row=44, sticky="W")
        ttk.Label(self.mainframe, text="< y <").grid(column=2, row=44, sticky="W")
        self.y_max = StringVar()
        self.y_max.set("50")
        y_max_entry = ttk.Entry(self.mainframe, width=5, textvariable=self.y_max).grid(column=3, row=44, sticky="W")
        ttk.Button(self.mainframe, text="apply", command=self.change_y_range).grid(column=4, row=44, sticky="W")

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
        ttk.Label(self.mainframe, text="x y z:").grid(column=0, row=45, sticky="E")
        self.x = StringVar()
        self.x.set("x")
        x_entry = ttk.Entry(self.mainframe, width=5, textvariable=self.x).grid(column=1, row=45, sticky="W")
        self.y = StringVar()
        self.y.set("y")
        y_entry = ttk.Entry(self.mainframe, width=5, textvariable=self.y).grid(column=2, row=45, sticky="W")
        self._z = StringVar()
        self._z.set("z")
        z_entry = ttk.Entry(self.mainframe, width=5, textvariable=self._z).grid(column=3, row=45, sticky="W")
        ttk.Button(self.mainframe, text="add waypoint", command=self.add_waypoint).grid(column=4, row=45, sticky="W")

        # グラフの準備
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.set_xlim(-50, 50)
        self.ax.set_ylim(-50, 50)
        self.ax.set_xlabel('Y[m]')
        self.ax.set_ylabel('X[m]')
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.content)
        self.canvas.get_tk_widget().grid(column=0, row=0, sticky="NWES")
        self.canvas.mpl_connect('button_press_event', self.onclick)

        for child in self.mainframe.winfo_children(): 
            child.grid_configure(padx=1, pady=1)
        # Windowを閉じたときの処理
        root.protocol("WM_DELETE_WINDOW", self._destroyWindow)


    def onclick(self, event):
        try:
            x, y, z = np.round(event.xdata), np.round(event.ydata), float(self.z.get())
        except ValueError:
            print("Z value is invalid")
            return
        if (x == None) or (y == None):
            return
        button = int(event.button)
        if button == 1: # Left click: add waypoint
            try:
                y_, x_, z_ = self._xyz[-1, :]
                if (x == x_) and (y_ == y) and (z_ == float(z)):
                    return
            except IndexError:
                pass
            self._xyz = np.append(self._xyz, np.array([[y, x, float(z)]]), axis=0)
            self.ax.plot(self._xyz[:, 1], self._xyz[:, 0], ".", color='red')
            self.draw_arrows(self._xyz.shape[0] - 1)
            self.draw_xy_list(self._xyz.shape[0])
        elif button == 3: # Right click: remove waypoint
            diff = self._xyz - np.array([y, x, float(z)]).T
            diff = np.linalg.norm(diff, axis=1)
            if diff.min() <= 2:
                index = diff.argmin()
                self._xyz = np.delete(self._xyz, index, axis=0)
            else:
                return
            self.redraw()


    # waypointにどの順番で向かうかを可視化する
    def draw_arrows(self, n):
        start = self._xyz[n - 1, :]
        end = self._xyz[n, :]
        start = np.array([start[1], start[0]])
        end = np.array([end[1], end[0]])
        self.ax.annotate(
                            '', xy=end, xytext=start,
                            arrowprops=dict(shrink=0, width=1, headwidth=8, 
                            headlength=10, connectionstyle='arc3',
                            facecolor='black', edgecolor='gray')
                        )
        self.canvas.draw_idle()



    # waypointを文字ベースでも可視化する
    def draw_xy_list(self, n):
        x, y, z = self._xyz[n - 1, :]
        lbl = ttk.Label(self.mainframe, text="{}:{}, {}, {}".format(n, x, y, z))
        lbl.grid(column=self.columnspan + 2, row=n, sticky="W")
        self.xyz_lbls.append(lbl)
    

    def clear_lbls(self):
        for i in self.xyz_lbls:
            i["text"] = ""

    
    # waypointを削除した時の処理
    def redraw(self):
        self.ax.cla()
        self.ax.set_ylim(int(self.x_min.get()), int(self.x_max.get()))
        self.ax.set_xlim(int(self.y_min.get()), int(self.y_max.get()))
        self.ax.set_xlabel('Y[m]')
        self.ax.set_ylabel('X[m]')
        self.ax.grid(True)
        self.ax.plot(self._xyz[:, 1], self._xyz[:, 0], ".", color='red')
        self.clear_lbls()
        for i in range(1, self._xyz.shape[0]): 
            self.draw_arrows(i)
        for i in range(1, self._xyz.shape[0] + 1):
            self.draw_xy_list(i)
        self.canvas.draw_idle()
        

    def change_x_range(self, *args):
        try:
            x_min, x_max = int(self.x_min.get()), int(self.x_max.get())
            self.ax.set_ylim(x_min, x_max)
            self.canvas.draw_idle()
        except ValueError:
            pass
    

    def change_y_range(self, *args):
        try:
            y_min, y_max = int(self.y_min.get()), int(self.y_max.get())
            self.ax.set_xlim(y_min, y_max)
            self.canvas.draw_idle()
        except ValueError:
            pass

    
    def clear(self, *args):
        self.ax.cla()
        self.ax.set_xlim(-50, 50)
        self.ax.set_ylim(-50, 50)
        self.ax.set_xlabel('Y[m]')
        self.ax.set_ylabel('X[m]')
        self.ax.grid(True)
        self.clear_lbls()
        self.canvas.draw_idle()
        self._xyz = np.empty((0, 3), int)
    

    def repeat(self, *args):
        try:
            n = int(self.n_repeat.get())
            xyzs = self._xyz
            if self._xyz.shape[0]:
                for _ in range(n):
                    for i in range(1, xyzs.shape[0]):
                        diffs = xyzs[i, :] - xyzs[i - 1, :]
                        y, x, z = diffs + self._xyz[-1, :]
                        self._xyz = np.append(self._xyz, np.array([[y, x, float(z)]]), axis=0)
                self.redraw()
        except ValueError:
            return


    def undo(self, *args):
        try:
            self._xyz = np.delete(self._xyz, - 1, axis=0)
            self.redraw()
        except IndexError:
            pass


    def add_waypoint(self, *args):
        try:
            x, y, z = float(self.x.get()), float(self.y.get()), float(self._z.get())
            self._xyz = np.append(self._xyz, np.array([[x, y, float(z)]]), axis=0)
            self.redraw()
        except ValueError:
            pass


    def to_json(self, *args):
        data = defaultdict(list)
        if not self._xyz.shape[0]:
            return
        for i, xyz in enumerate(self._xyz):
            x, y, z = xyz
            d = {'ID':i, 'X': x, 'Y': y, 'Z': z}
            data["waypoints"].append(d)
        with open('./mission.json', mode='wt', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)


    def _destroyWindow(self):
        root.quit()
        root.destroy()



root = Tk()
MissionGenerator(root)
root.mainloop()
