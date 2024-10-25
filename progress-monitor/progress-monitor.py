#!/usr/bin/env python3

import re
import os
import threading
from datetime import datetime, timedelta
import webbrowser

import tkinter as tk
from tkinter import ttk, filedialog, font, messagebox

language_config_dict = {
    "en": {
        "app_title": "Progress Monitor",
        "file_title": "File:",
        "progress_title": "Progress: ",
        "time_left_title": "Remaining Time: ",
        "eta_title": "Completion Time: ",
        "error_cnt_title": "Error Count: ",
        "warning_cnt_title": "Warning Count: ",
        "first_error_title": "First Error Line: ",
        "browse_btn": "Browse",
        "start_btn": "Start",
        "stop_btn": "Stop",
        "reset_btn": "Reset",
        "calculate_inline_msg": "Calculating",
        "read_start_msg": "Reading file",
        "monitor_start_msg": "Monitoring file",
        "monitor_exception_msg": "Exception occurred while monitoring file",
        "select_file_msg": "Please select a file",
        "file_not_exist_msg": "The file does not exist",
        "find_error_msg": "An error was detected",
        "find_warning_msg": "A warning was detected",
        "find_nan_inf_msg": "NAN/INF detected as an error",
        "find_end_msg": "END/FINISH detected as an end of monitoring",
        "timestamp_match_failed_msg": "Timestamp matching failed",
        "timestamp_parse_failed_msg": "Timestamp parsing failed",
        "pct_match_failed_msg": "Percentage matching failed",
        "pct_parse_failed_msg": "Percentage parsing failed",
        "pct_range_error_msg": "out of range",
        "error": "ERROR",
        "warning": "WARNING",
        "info": "INFO",
        "options_menu": "Options",
        "language_menu": "Language",
        "timestamp_format_menu": "Timestamp",
        "about_menu": "About",
        "help_menu": "Help",
        "repository_menu": "Repository",
    },
    "cn": {
        "app_title": "进度监控器",
        "file_title": "文件：",
        "progress_title": "进度：",
        "time_left_title": "剩余时间：",
        "eta_title": "完成时间：",
        "error_cnt_title": "错误统计：",
        "warning_cnt_title": "警告统计：",
        "first_error_title": "第一个错误行：",
        "browse_btn": "浏览",
        "start_btn": "开始",
        "stop_btn": "停止",
        "reset_btn": "重置",
        "calculate_inline_msg": "计算中",
        "read_start_msg": "读取文件",
        "monitor_start_msg": "监控文件",
        "monitor_exception_msg": "监控文件时发生了异常",
        "select_file_msg": "请选择一个文件",
        "file_not_exist_msg": "文件不存在",
        "find_error_msg": "检测到一个错误",
        "find_warning_msg": "检测到一个警告",
        "find_nan_inf_msg": "检测到NAN/INF并视为错误",
        "find_end_msg": "检测到END/FINISH并视为监控结束",
        "timestamp_match_failed_msg": "时间戳匹配失败",
        "timestamp_parse_failed_msg": "时间戳解析失败",
        "pct_match_failed_msg": "进度匹配失败",
        "pct_parse_failed_msg": "进度解析失败",
        "pct_range_error_msg": "超出合理范围",
        "error": "错误",
        "warning": "警告",
        "info": "信息",
        "options_menu": "选项",
        "language_menu": "语言",
        "timestamp_format_menu": "时间戳",
        "about_menu": "关于",
        "help_menu": "帮助",
        "repository_menu": "仓库",
    },
}

timestamp_format_list = ["%Y-%m-%d %H:%M:%S.%f", "%Y/%m/%d %H:%M:%S.%f", "%H:%M:%S.%f"]


class ProgressMonitorApp:

    def __init__(self, root):
        self.root = root
        self.current_language = tk.StringVar(value="en")
        self.texts = language_config_dict[self.current_language.get()]
        self.root.title(self.texts["app_title"])
        self.timestamp_format = tk.StringVar(value="%Y-%m-%d %H:%M:%S.%f")

        self.init_reset_data(init_flag=True)
        self.create_widgets()
        self.create_menu()

    def create_menu(self):
        # 创建菜单栏
        self.menu_bar = tk.Menu(self.root)

        # 创建选项菜单
        self.option_menu = tk.Menu(self.menu_bar, tearoff=0)

        # 创建语言子菜单
        self.language_menu = tk.Menu(self.option_menu, tearoff=0)
        self.language_menu.add_radiobutton(
            label="English",
            variable=self.current_language,
            value="en",
            command=lambda: self.change_language("en"),
        )
        self.language_menu.add_radiobutton(
            label="中文",
            variable=self.current_language,
            value="cn",
            command=lambda: self.change_language("cn"),
        )
        self.option_menu.add_cascade(
            label=self.texts["language_menu"], menu=self.language_menu
        )

        # 创建时间戳子菜单
        self.timestamp_format_menu = tk.Menu(self.option_menu, tearoff=0)
        for item in timestamp_format_list:
            self.timestamp_format_menu.add_radiobutton(
                label=item,
                variable=self.timestamp_format,
                value=item,
                command=self.clear_after_change_timestamp_format,
            )
        self.option_menu.add_cascade(
            label=self.texts["timestamp_format_menu"],
            menu=self.timestamp_format_menu,
        )

        # 创建帮助菜单
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(
            label=self.texts["repository_menu"], command=self.show_help
        )
        self.help_menu.add_command(
            label=self.texts["about_menu"], command=self.show_about
        )

        self.menu_bar.add_cascade(
            label=self.texts["options_menu"], menu=self.option_menu
        )
        self.menu_bar.add_cascade(label=self.texts["help_menu"], menu=self.help_menu)
        self.root.config(menu=self.menu_bar)

    def create_widgets(self):
        # 主窗口划分为5行，对应不同的缩放权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=0)
        self.root.rowconfigure(2, weight=0)
        self.root.rowconfigure(3, weight=0)
        self.root.rowconfigure(4, weight=2)

        # 控制部分

        # 控制部分框架，占据主窗口的第一行
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        control_frame.columnconfigure(1, weight=1)

        # 文件选择标签，占据控制部分框架的第一行第一列
        self.file_title = ttk.Label(control_frame, text=self.texts["file_title"])
        self.file_title.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        # 文件选择输入框，占据控制部分框架的第一行第二列
        ttk.Entry(control_frame, textvariable=self.file_path).grid(
            row=0, column=1, padx=5, pady=5, sticky="ew"
        )
        # 文件选择按钮，占据控制部分框架的第一行第三列
        self.file_btn = ttk.Button(
            control_frame,
            text=self.texts["browse_btn"],
            command=self.click_to_browse_file,
        )
        self.file_btn.grid(row=0, column=2, padx=5, pady=5)

        # 控制按钮框架，占据控制部分框架的第二行（跨越三列）
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        # 开始/停止按钮，占据控制按钮框架的第一行第二列
        self.start_stop_btn = ttk.Button(
            button_frame,
            text=self.texts["start_btn"],
            command=self.click_to_start_stop_monitoring,
        )
        self.start_stop_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # 重置按钮，占据控制按钮框架的第一行第三列
        self.reset_btn = ttk.Button(
            button_frame,
            text=self.texts["reset_btn"],
            command=self.click_to_reset_monitoring,
        )
        self.reset_btn.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        # 进度信息部分

        # 进度信息框架，占据主窗口的第四行，两列的权重不一样
        info_frame = ttk.Frame(self.root, padding="10")
        info_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        info_frame.columnconfigure(0, weight=0)
        info_frame.columnconfigure(1, weight=1)

        # 进度百分比标签，占据进度信息框架的第一行第一列
        self.progress_title = ttk.Label(
            info_frame, text=self.texts["progress_title"], anchor="w"
        )
        self.progress_title.grid(row=0, column=0, pady=5, sticky="w")
        # 剩余时间标签，占据进度信息框架的第一行第二列
        self.time_left_title = ttk.Label(
            info_frame, text=self.texts["time_left_title"], anchor="w"
        )
        self.time_left_title.grid(row=1, column=0, pady=5, sticky="w")
        # 目标完成时间标签，占据进度信息框架的第一行第三列
        self.eta_title = ttk.Label(info_frame, text=self.texts["eta_title"], anchor="w")
        self.eta_title.grid(row=2, column=0, pady=5, sticky="w")
        # 第一个错误标签，占据进度信息框架的第一行第四列
        self.first_error_title = ttk.Label(
            info_frame, text=self.texts["first_error_title"], anchor="w"
        )
        self.first_error_title.grid(row=3, column=0, pady=5, sticky="w")
        # 错误总数标签，占据进度信息框架的第一行第五列
        self.error_cnt_title = ttk.Label(
            info_frame, text=self.texts["error_cnt_title"], anchor="w"
        )
        self.error_cnt_title.grid(row=4, column=0, pady=5, sticky="w")
        # 警告总数标签，占据进度信息框架的第一行第六列
        self.warning_cnt_title = ttk.Label(
            info_frame, text=self.texts["warning_cnt_title"], anchor="w"
        )
        self.warning_cnt_title.grid(row=5, column=0, pady=5, sticky="w")

        # 进度百分比内容，占据进度信息框架的第一行第二列
        self.cur_progress_label = ttk.Label(info_frame, text="  0.00%", anchor="w")
        self.cur_progress_label.grid(row=0, column=1, pady=5, sticky="w")

        # 剩余时间内容，占据进度信息框架的第二行第二列
        self.time_left_label = ttk.Label(info_frame, text="", anchor="w")
        self.time_left_label.grid(row=1, column=1, pady=5, sticky="w")

        # 目标完成时间内容，占据进度信息框架的第三行第二列
        self.eta_label = ttk.Label(info_frame, text="", anchor="w")
        self.eta_label.grid(row=2, column=1, pady=5, sticky="w")

        # 第一个错误内容，占据进度信息框架的第四行第二列
        self.first_error_label = ttk.Label(
            info_frame, text="", foreground="red", anchor="w"
        )
        self.first_error_label.grid(row=3, column=1, pady=5, sticky="w")

        # 错误总数内容，占据进度信息框架的第五行第二列
        self.error_cnt_label = ttk.Label(info_frame, text="0", anchor="w")
        self.error_cnt_label.grid(row=4, column=1, pady=5, sticky="w")

        # 警告总数内容，占据进度信息框架的第六行第二列
        self.warning_cnt_label = ttk.Label(info_frame, text="0", anchor="w")
        self.warning_cnt_label.grid(row=5, column=1, pady=5, sticky="w")

        # 进度条组件，占据进度信息框架的第七行第一列（跨越两列）
        self.progress_bar = ttk.Progressbar(
            info_frame, orient="horizontal", mode="determinate"
        )
        self.progress_bar.grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")

        # 日志输出部分

        # 日志输出框架，占据主窗口的第五行
        log_frame = ttk.Frame(self.root, padding="10")
        log_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # 日志输出文本框，占据日志输出框架的第一行
        self.log_text = tk.Text(log_frame, wrap="word", state="disabled")
        self.log_text.grid(row=0, column=0, sticky="nsew")

        # 文本框附带纵向滚动条
        log_scroll = ttk.Scrollbar(
            log_frame, orient="vertical", command=self.log_text.yview
        )
        self.log_text["yscrollcommand"] = log_scroll.set
        log_scroll.grid(row=0, column=1, sticky="ns")

        # 文本框内容样式标签（对应不同的字体颜色）
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("info", foreground="green")

    def click_to_browse_file(self):
        initial_dir = os.getcwd()
        file_path = filedialog.askopenfilename(
            initialdir=initial_dir,
            filetypes=[
                ("Log Files", "*.log"),
                ("Txt Files", "*.txt"),
                ("All Files", "*.*"),
            ],
        )

        if file_path:
            self.file_path.set(file_path)

    def click_to_start_stop_monitoring(self):
        if self.check_monitor_thread_alive():
            self.stop_monitor_thread_if_alive_and_join()

        else:
            self.try_start_monitor_thread()

        self.update_start_stop_btn_ui()

    def click_to_reset_monitoring(self):

        self.stop_monitor_thread_if_alive_and_join()

        self.init_reset_data(init_flag=False)

        self.update_start_stop_btn_ui()
        self.update_main_info_ui()
        self.update_extra_info_ui()
        self.clear_log_text()

    def init_reset_data(self, init_flag: bool):
        self.last_time_stamp = None
        self.last_pct = None
        self.speed = None
        self.pct = 0
        self.time_left_str = ""
        self.eta_str = ""

        self.check_data = {
            "ERROR": 0,
            "WARNING": 0,
            "FIRST_ERROR": "",
        }

        if init_flag:
            self.file_path = tk.StringVar()
            self.stop_event = threading.Event()
            self.monitor_thread = None

    def progress_detection(self, line: str):
        try:
            time_stamp = self.parse_timestamp_from_string(line)
        except Exception as err:
            self.log_msg(err.__str__(), tag="warning")
            # use current time instead
            time_stamp = datetime.now()

        try:
            pct = self.parse_percentage_from_string(line)
        except Exception as err:
            self.log_msg(err.__str__(), tag="warning")
            # use current percentage instead
            pct = self.pct

        self.progress_update(pct, time_stamp)
        self.update_main_info_ui()

    def progress_update(self, pct: float, time_stamp: datetime):
        if (self.last_time_stamp is None) or (self.last_pct is None):
            self.pct = pct
            self.time_left_str = self.texts["calculate_inline_msg"]
            self.eta_str = self.texts["calculate_inline_msg"]
        else:
            time_delta = (time_stamp - self.last_time_stamp).total_seconds()
            pct_delta = pct - self.last_pct

            if time_delta > 0 and pct_delta > 0:
                self.pct = pct

                speed = self.update_and_get_speed(pct_delta / time_delta)
                time_left = (1 - pct) / speed
                self.time_left_str = self.get_time_left_str(time_left)

                eta = time_stamp + timedelta(seconds=time_left)
                self.eta_str = self.get_eta_str(eta)

        self.last_time_stamp = time_stamp
        self.last_pct = pct

    def keyword_detection_and_update(self, line: str):
        upper_line = line.upper()
        change_flag = False

        if "ERROR" in upper_line:
            self.check_data["ERROR"] += 1
            self.log_msg(self.texts["find_error_msg"], tag="error")
            change_flag = True
            if not self.check_data["FIRST_ERROR"]:
                self.check_data["FIRST_ERROR"] = line

        if ("NAN" in upper_line) or ("INF" in upper_line):
            self.check_data["ERROR"] += 1
            self.log_msg(self.texts["find_nan_inf_msg"], tag="error")
            change_flag = True
            if not self.check_data["FIRST_ERROR"]:
                self.check_data["FIRST_ERROR"] = line

        if "WARNING" in upper_line:
            self.check_data["WARNING"] += 1
            self.log_msg(self.texts["find_warning_msg"], tag="warning")
            change_flag = True

        if change_flag:
            self.update_extra_info_ui()

    def end_detection(self, line: str) -> bool:
        if any(item in line.upper() for item in ("END", "FINISH")):
            self.log_msg(self.texts["find_end_msg"], tag="info")
            return True

        return False

    def read_loop(self, file_path: str):
        self.log_msg(head=self.texts["read_start_msg"], msg=file_path, tag="info")
        with open(file_path, "r") as file:
            file.seek(0, os.SEEK_END)

            while not self.stop_event.is_set():
                line = file.readline()
                if not line:
                    continue

                self.log_msg(line.strip())
                self.progress_detection(line)
                self.keyword_detection_and_update(line)

                if self.end_detection(line):
                    break

    def monitor_loop(self, file_path: str):
        self.log_msg(head=self.texts["monitor_start_msg"], msg=file_path, tag="info")

        while not self.stop_event.is_set():
            try:
                self.read_loop(file_path)
            except Exception as e:
                self.log_msg(
                    head=self.texts["monitor_exception_msg"],
                    msg=f"\n{e}",
                    tag="error",
                )

                self.stop_event.set()
                break

    def parse_timestamp_from_string(self, input_str: str) -> datetime:
        """
        Get a high-precision timestamp.\n
        The timestamp must be wrapped in [].\n
        For example, [2024-07-26 17:56:56.532]\n
        An exception will be thrown if the acquisition fails
        """

        timestamp_pattern = r"\[([\d:./\s_-]+)\]"
        match_results = re.search(timestamp_pattern, input_str)

        if not match_results:
            raise RuntimeError(self.texts["timestamp_match_failed_msg"])

        timestamp_str = match_results.group(1)
        try:
            timestamp_format = self.timestamp_format.get()
            parsed_timestamp = datetime.strptime(timestamp_str, timestamp_format)
            return parsed_timestamp
        except ValueError:
            raise RuntimeError(self.texts["timestamp_parse_failed_msg"])

    def parse_percentage_from_string(self, input_str: str) -> float:
        """
        Get percentage data, which must contain the % symbol\n
        For example, 40.00%\n
        An exception will be thrown if the acquisition fails\n
        Percentage data that is not in the range of 0-1 is also considered an error
        """

        percentage_pattern = r"(\d+(\.\d+)?)%"
        match_results = re.search(percentage_pattern, input_str)

        if not match_results:
            raise RuntimeError(self.texts["pct_match_failed_msg"])

        percentage_str = match_results.group(1)
        try:
            percentage_float = float(percentage_str) / 100.0
            if 0 <= percentage_float <= 1:
                return percentage_float
            else:
                raise RuntimeError(
                    f"{percentage_float} self.texts['pct_out_of_range_msg']"
                )
        except ValueError:
            raise RuntimeError(self.texts["pct_parse_failed_msg"])

    def clear_log_text(self):
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

    def update_title_and_btn_ui(self):
        self.root.title(self.texts["app_title"])
        self.file_title.config(text=self.texts["file_title"])
        self.progress_title.config(text=self.texts["progress_title"])
        self.time_left_title.config(text=self.texts["time_left_title"])
        self.eta_title.config(text=self.texts["eta_title"])
        self.first_error_title.config(text=self.texts["first_error_title"])
        self.error_cnt_title.config(text=self.texts["error_cnt_title"])
        self.warning_cnt_title.config(text=self.texts["warning_cnt_title"])

        self.file_btn.config(text=self.texts["browse_btn"])
        self.start_stop_btn.config(text=self.texts["start_btn"])
        self.reset_btn.config(text=self.texts["reset_btn"])

    def update_menu_ui(self):
        self.menu_bar.entryconfig(1, label=self.texts["options_menu"])
        self.menu_bar.entryconfig(2, label=self.texts["help_menu"])

        self.option_menu.entryconfig(0, label=self.texts["language_menu"])
        self.option_menu.entryconfig(1, label=self.texts["timestamp_format_menu"])

        self.help_menu.entryconfig(0, label=self.texts["repository_menu"])
        self.help_menu.entryconfig(1, label=self.texts["about_menu"])

    def update_start_stop_btn_ui(self):
        if self.check_monitor_thread_alive():
            self.start_stop_btn.config(text=self.texts["stop_btn"])
        else:
            self.start_stop_btn.config(text=self.texts["start_btn"])

    def update_main_info_ui(self):
        pct_num = self.pct * 100

        self.cur_progress_label.config(text=f"{pct_num:6.2f}%")
        self.time_left_label.config(text=self.time_left_str)
        self.eta_label.config(text=self.eta_str)
        self.progress_bar["value"] = pct_num

    def update_extra_info_ui(self):
        self.first_error_label.config(text=self.check_data["FIRST_ERROR"])
        self.error_cnt_label.config(text=str(self.check_data["ERROR"]))
        self.warning_cnt_label.config(text=str(self.check_data["WARNING"]))

    def get_eta_str(self, eta: datetime) -> str:
        timestamp_format = self.timestamp_format.get()
        eta_str = eta.strftime(timestamp_format)
        return eta_str

    def get_time_left_str(self, time_left: float) -> str:
        hours, remainder = divmod(time_left, 3600)
        minutes, seconds = divmod(remainder, 60)

        time_left_str = ""
        if hours > 0:
            time_left_str += f"{int(hours):2}h "
        if minutes > 0:
            time_left_str += f"{int(minutes):2}m "
        if seconds > 0 or time_left_str == "":
            time_left_str += f"{int(seconds):2}s "

        return time_left_str

    def update_and_get_speed(self, new_speed: float) -> float:
        SMOOTHALPHA = 0.4

        if self.speed is None:
            self.speed = new_speed
        else:
            self.speed = SMOOTHALPHA * new_speed + (1 - SMOOTHALPHA) * self.speed
        return self.speed

    def log_msg(self, msg: str, head: str | None = None, tag: str | None = None):
        self.log_text.config(state="normal")

        if head:
            msg = f"{head} {msg}"

        if tag:
            tag_name = self.texts[tag]
            self.log_text.insert(tk.END, f"[{tag_name}] {msg}\n", tag)
        else:
            self.log_text.insert(tk.END, f"{msg}\n")

        self.log_text.config(state="disabled")
        self.log_text.yview(tk.END)

    def check_monitor_thread_alive(self):
        return self.monitor_thread and self.monitor_thread.is_alive()

    def try_start_monitor_thread(self):
        file_path = self.file_path.get()
        if not file_path:
            self.log_msg(self.texts["select_file_msg"], tag="error")
            return

        if not os.path.exists(file_path):
            self.log_msg(
                head=self.texts["file_not_exist_msg"],
                msg=file_path,
                tag="error",
            )
            return

        self.stop_event.clear()
        self.monitor_thread = threading.Thread(
            target=self.monitor_loop, args=(file_path,)
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitor_thread_if_alive_and_join(self):
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.stop_event.set()
            self.monitor_thread.join()

    def change_language(self, language: str):
        self.current_language.set(language)
        self.texts = language_config_dict[language]
        self.update_title_and_btn_ui()
        self.update_start_stop_btn_ui()
        self.update_main_info_ui()
        self.update_extra_info_ui()
        self.update_menu_ui()

    def clear_after_change_timestamp_format(self):
        self.last_time_stamp = None
        self.speed = None

    def show_help(self):
        url = "https://github.com/fenglielie/toolbox"
        webbrowser.open(url)

    def show_about(self):
        about_texts = {
            "en": (
                "Progress Monitor\n\n"
                "This is a Python Tkinter-based GUI tool script for monitoring progress information in log files,"
                "providing corresponding statistics and display functions.\n\n"
                "fenglielie@qq.com"
            ),
            "cn": (
                "进度监视器\n\n"
                "这是一个基于 Python Tkinter 的 GUI 工具脚本，"
                "用于监控日志文件中的进度信息，提供相应的统计和显示功能。\n\n"
                "fenglielie@qq.com"
            ),
        }

        about_text = about_texts[self.current_language.get()]
        messagebox.showinfo(self.texts["about_menu"], about_text)

    def close(self):
        self.stop_monitor_thread_if_alive_and_join()
        self.root.destroy()


def configure_tkinter_fonts():
    font.nametofont("TkDefaultFont").configure(size=12)
    font.nametofont("TkTextFont").configure(size=12)
    font.nametofont("TkFixedFont").configure(size=12)
    font.nametofont("TkMenuFont").configure(size=12)
    font.nametofont("TkHeadingFont").configure(size=12)
    font.nametofont("TkCaptionFont").configure(size=12)
    font.nametofont("TkSmallCaptionFont").configure(size=12)
    font.nametofont("TkIconFont").configure(size=12)


def configure_tkinter_gui_size(root):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    pos_x = int((screen_width - 600) / 2)
    pos_y = int((screen_height - 900) / 2)
    root.geometry(f"600x800+{pos_x}+{pos_y}")


def main():
    root = tk.Tk()

    configure_tkinter_fonts()

    app = ProgressMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)

    configure_tkinter_gui_size(root)

    root.mainloop()


if __name__ == "__main__":
    main()
