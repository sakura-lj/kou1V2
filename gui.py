# -*- coding: utf-8 -*-
import datetime
import time
import tkinter as tk
from tkinter import messagebox
import subprocess
import json
import os
import sys

import threading
import signal
import psutil

data_path = os.path.join(os.path.dirname(sys.executable), "_internal",'data.json')
#data_path = os.path.join(os.path.dirname(sys.executable),'data.json')
# os.environ['DATA_PATH'] = data_path

try:
    print(data_path)
except Exception as e:
    print(f"Error reading data: {e}")


class BotThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(BotThread, self).__init__(*args, **kwargs)
        self.daemon = True  # 设置线程为守护线程，确保主程序退出时自动终止
        self.process = None  # 存储子进程对象
        self.stopped = threading.Event()  # 创建一个事件标志，用于指示线程是否已停止

    def run(self):
        # 获取 bot.exe 的路径
        bot_path = os.path.join(os.path.dirname(sys.executable), "_internal", 'bot.exe')

        # 检查 bot.exe 是否存在
        if not os.path.exists(bot_path):
            print(f"Error: {bot_path} does not exist.")
            return

        # 使用创建新进程组的标志启动 bot.exe 进程
        self.process = subprocess.Popen([bot_path], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        # 等待子进程完成
        self.process.wait()
        # 当进程结束时，设置事件标志为已停止
        self.stopped.set()

    def stop(self):
        try:
            if self.process is not None:
                parent = psutil.Process(self.process.pid)  # 获取父进程对象
                for child in parent.children(recursive=True):  # 递归获取所有子进程
                    child.terminate()  # 尝试终止子进程

                parent.terminate()  # 终止父进程

                # 等待子进程终止，设置超时时间为3秒
                gone, still_alive = psutil.wait_procs(parent.children(recursive=True), timeout=3)
                for p in still_alive:
                    p.kill()  # 强制终止仍在运行的子进程
                parent.kill()  # 强制终止父进程
        except psutil.NoSuchProcess:
            print("The process does not exist or is already terminated.")
        except Exception as e:
            print(f"An error occurred while stopping the process: {e}")
        finally:
            self.stopped.set()  # 设置事件，表示进程已经停止

        # 确保进程对象被清理
        self.process = None

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master    # 设置主窗口
        self.pack(padx=10, pady=10)   # 设置窗口的外边距
        self.create_widgets()   # 创建窗口的控件
        self.process = None # 存储子进程对象
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)   # 设置关闭窗口时的
        self.is_running = False  # 添加一个标志位，表示程序是否正在运行
        self.start_time = datetime.datetime.now()  # 记录程序开始运行的时间

    def create_widgets(self):
        self.create_labels_entries()    # 创建标签和输入框
        self.create_buttons()   # 创建按钮
        self.create_status_text()   # 创建状态文本框
        self.create_info_text() # 创建信息文本框

    def create_labels_entries(self):    # 创建标签和输入框
        self.qq_label = tk.Label(self, text="你的QQ小号:")  # 创建一个标签
        self.qq_label.grid(row=0, column=0, pady=5, sticky='e') # 将标签放置在窗口中
        self.qq_entry = tk.Entry(self)  # 创建一个输入框
        self.qq_entry.grid(row=0, column=1, pady=5) # 将输入框放置在窗口中

        self.keyword_label = tk.Label(self, text="抢活关键词:")
        self.keyword_label.grid(row=1, column=0, pady=5, sticky='e')
        self.keyword_entry = tk.Entry(self)
        self.keyword_entry.grid(row=1, column=1, pady=5)

        self.group_label = tk.Label(self, text="抢活目标群号:")
        self.group_label.grid(row=2, column=0, pady=5, sticky='e')
        self.group_entry = tk.Entry(self)
        self.group_entry.grid(row=2, column=1, pady=5)

        self.send_label = tk.Label(self, text="你想扣什么:")
        self.send_label.grid(row=3, column=0, pady=5, sticky='e')
        self.send_entry = tk.Entry(self)
        self.send_entry.grid(row=3, column=1, pady=5)

    def create_buttons(self):
        self.add_button = tk.Button(self, text="添加规则", command=lambda: self.modify_rule('add'))
        self.add_button.grid(row=3, column=2, pady=5, sticky='ew')

        self.delete_button = tk.Button(self, text="删除规则", command=lambda: self.modify_rule('delete'))
        self.delete_button.grid(row=3, column=3, pady=5, sticky='ew')

        self.change_button = tk.Button(self, text="更改QQ号", command=self.change_qq)
        self.change_button.grid(row=0, column=3, pady=5, sticky='ew')

        # self.add_keyword_button = tk.Button(self, text="添加关键词", command=self.add_keyword)
        # self.add_keyword_button.grid(row=1, column=2, pady=5, sticky='ew')

        # self.delete_keyword_button = tk.Button(self, text="删除关键词", command=self.delete_keyword)
        # self.delete_keyword_button.grid(row=1, column=3, pady=5, sticky='ew')

        # self.add_group_button = tk.Button(self, text="添加群号", command=self.add_group)
        # self.add_group_button.grid(row=2, column=2, pady=5, sticky='ew')

        # self.delete_group_button = tk.Button(self, text="删除群号", command=self.delete_group)
        # self.delete_group_button.grid(row=2, column=3, pady=5, sticky='ew')

        self.start_button = tk.Button(self, text="开始抢活！", command=self.start_bot)
        self.start_button.grid(row=4, column=0, pady=5, sticky='ew')

        self.stop_button = tk.Button(self, text="停止抢活！", command=self.stop_bot)
        self.stop_button.grid(row=4, column=1, pady=5, sticky='ew')

    def create_status_text(self):
        self.status_text = tk.Text(self, height=5, width=50)    # 创建一个文本框
        self.status_text.grid(row=5, column=0, columnspan=4, pady=10)   # 将文本框放置在窗口中
        
    def create_info_text(self):
        self.group_info_text = tk.Text(self, height=5, width=50)
        self.group_info_text.grid(row=6, column=0, columnspan=4, pady=10)
        self.group_info_text.insert(tk.END, "当前检测的所有群号与反馈的QQ号还有发送词:\n")

        # self.keyword_info_text = tk.Text(self, height=5, width=50)
        # self.keyword_info_text.grid(row=7, column=0, columnspan=4, pady=10)
        # self.keyword_info_text.insert(tk.END, "目前检测的所有关键词:\n")

        # self.status_info_text = tk.Text(self, height=16, width=50)
        # self.status_info_text.grid(row=8, column=0, columnspan=4, pady=10)
        # self.status_info_text.insert(tk.END, "使用提示！！！(必看):\n\n1.首先设置你的QQ小号，这是当机器人自动扣了活以后，会像该QQ号发送是否撤回提示。可以设置成QQ小号，或者男/女朋友的号，当然也可以不设置。\n2.设置抢活关键词，一次只能设置一个，可以多次设置。这个你可以看你们组长每次发任务时一般会有个什么重复出现的词语或句子\n3.设置检测的群号，就是你们支部派任务的群，该脚本只会在你设置的群号里面扣发送词，也可以设置多个。\n4.设置你想扣什么，就是在指定群聊检测到关键词时扣什么例如：1，你可更改为数字，中文以及等等。\n\n有bug可以反馈邮箱2900153778@qq.com或者github提issues，反馈时请截屏错误提示。\n因为使用了pyinstaller打包，可能报毒，但是源码全部开源在github:https://github.com/sakura-lj/kou1V2，可以自行审查")
            # 添加标签配置
        self.status_info_text = tk.Text(self, height=18, width=50)
        self.status_info_text.grid(row=8, column=0, columnspan=4, pady=10)
        self.status_info_text.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))
        self.status_info_text.tag_configure("italic", font=("TkDefaultFont", 10, "italic"))
        
        # 插入带格式的文本
        self.status_info_text.insert(tk.END, "使用提示！！！(必看):\n\n", "bold")
        self.status_info_text.insert(tk.END, "1.", "bold")
        self.status_info_text.insert(tk.END, "首先设置你的QQ小号，这是当机器人自动扣了活以后，会像该QQ号发送是否撤回提示。可以设置成QQ小号，或者男/女朋友的号，当然也可以不设置。\n")
        self.status_info_text.insert(tk.END, "2.", "bold")
        self.status_info_text.insert(tk.END, "设置抢活关键词，一次只能设置一个，可以多次设置。这个你可以看你们组长每次发任务时一般会有个什么重复出现的词语或句子\n")
        self.status_info_text.insert(tk.END, "3.", "bold")
        self.status_info_text.insert(tk.END, "设置检测的群号，就是你们支部派任务的群，该脚本只会在你设置的群号里面扣发送词，也可以设置多个。\n")
        self.status_info_text.insert(tk.END, "4.", "bold")
        self.status_info_text.insert(tk.END, "设置你想扣什么，就是在指定群聊检测到关键词时扣什么例如：1，你可更改为数字，中文以及等等。\n\n")
        
        self.status_info_text.insert(tk.END, "有bug可以反馈邮箱")
        self.status_info_text.insert(tk.END, "2900153778@qq.com")
        self.status_info_text.insert(tk.END, "或者github提issues，反馈时请截屏错误提示。\n")
        self.status_info_text.insert(tk.END, "因为使用了pyinstaller打包，可能报毒，但是源码全部开源在")
        self.status_info_text.insert(tk.END, "github:https://github.com/sakura-lj/kou1V2")
        self.status_info_text.insert(tk.END, "，可以自行审查",)
    def on_closing(self):
        if self.is_running:  # 如果程序正在运行，弹出警告消息
            messagebox.showwarning("警告", "请先停止抢活再退出")
        else:  # 否则，正常关闭窗口
            self.master.destroy()
    
    def modify_rule(self, action='add'):
        """统一处理规则的添加和删除"""
        if self.is_running:
            messagebox.showwarning("警告", "正在抢活中，请先停止抢活再进行数据修改")
            return
            
        # 获取输入值
        group = self.group_entry.get().strip()
        keyword = self.keyword_entry.get().strip()
        send_word = self.send_entry.get().strip()
        
        # 验证输入
        if not all([group, keyword, send_word]):
            messagebox.showwarning("输入错误", "请填写完整的规则信息")
            return
                
        try:
            data = self.load_data()
            
            if action == 'add':
                # 检查完全相同的规则
                for rule in data['checks']:
                    if rule['group'] == group and rule['keyword'] == keyword:
                        messagebox.showwarning("添加失败", "该规则已存在")
                        return
                
                # 检查关键词子集
                subset_rules = []
                for rule in data['checks']:
                    if rule['group'] == group:
                        # 检查新关键词是否是现有关键词的子集
                        if keyword in rule['keyword']:
                            subset_rules.append((rule['keyword'], '子集'))
                        # 检查现有关键词是否是新关键词的子集
                        elif rule['keyword'] in keyword:
                            subset_rules.append((rule['keyword'], '父集'))
                
                if subset_rules:
                    warning_msg = "发现以下关键词可能会产生冲突：\n\n"
                    for rule_keyword, relation in subset_rules:
                        warning_msg += f"- '{rule_keyword}' (作为{relation})\n"
                    warning_msg += "\n这可能会导致多次触发，是否继续添加？"
                    
                    if messagebox.askyesno("关键词冲突警告", warning_msg):
                        # 用户选择继续添加
                        new_rule = {
                            "group": group,
                            "keyword": keyword,
                            "send_word": send_word
                        }
                        data['checks'].append(new_rule)
                        
                        # 询问是否要删除冲突的规则
                        if messagebox.askyesno("删除确认", 
                            "是否要删除冲突的规则？\n(建议保留更长的关键词，删除更短的关键词)"):
                            # 删除冲突的规则
                            data['checks'] = [
                                rule for rule in data['checks']
                                if not (rule['group'] == group and 
                                    rule['keyword'] in [kw for kw, _ in subset_rules])
                            ]
                            # 重新添加新规则
                            data['checks'].append(new_rule)
                            message = "规则已添加，并删除了冲突的规则"
                        else:
                            message = "规则已添加，保留了所有规则"
                    else:
                        return
                else:
                    # 没有冲突，直接添加
                    new_rule = {
                        "group": group,
                        "keyword": keyword,
                        "send_word": send_word
                    }
                    data['checks'].append(new_rule)
                    message = "规则添加成功"
                    
            else:  # delete
                # 查找并删除匹配的规则
                original_length = len(data['checks'])
                data['checks'] = [rule for rule in data['checks'] 
                                if not (rule['group'] == group and 
                                    rule['keyword'] == keyword and 
                                    rule['send_word'] == send_word)]
                
                if len(data['checks']) == original_length:
                    messagebox.showwarning("删除失败", "未找到匹配的规则")
                    return
                message = "规则删除成功"
                
            # 保存更改
            self.save_data(data)
            messagebox.showinfo("成功", message)
            self.status_text.insert(tk.END, f"{message}\n")
            self.update_info_display()  # 更新显示
            
        except Exception as e:
            messagebox.showerror("错误", f"操作失败: {str(e)}")


    def change_qq(self):
        """修改反馈QQ号"""
        if self.is_running:
            messagebox.showwarning("警告", "正在抢活中，请先停止抢活再进行数据修改")
            return
            
        qq = self.qq_entry.get().strip()
        if not qq:
            messagebox.showwarning("输入错误", "请输入有效的QQ号")
            return
            
        try:
            data = self.load_data()
            data['FeedBackqq'] = qq
            self.save_data(data)
            messagebox.showinfo("成功", "反馈QQ号已更新")
            self.status_text.insert(tk.END, "反馈QQ号已更新\n")
            self.update_info_display()
        except Exception as e:
            messagebox.showerror("错误", f"更新QQ号失败: {str(e)}")
    
    def load_data(self):
        """加载配置数据"""
        try:
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.update_info_display(data)
                    return data
            else:
                # 返回默认配置
                return {
                    "FeedBackqq": "",
                    "checks": [],
                    "start_date": datetime.datetime.now().strftime('%Y-%m-%d')
                }
        except Exception as e:
            print(f"加载配置失败: {e}")
            return None

    def update_info_display(self, data=None):
        """更新信息显示"""
        if data is None:
            data = self.load_data()
        
        if data:
            # 更新群组信息显示
            self.group_info_text.delete(1.0, tk.END)
            self.group_info_text.insert(tk.END, "当前所有规则:\n")
            for rule in data['checks']:
                self.group_info_text.insert(tk.END, 
                    f"群号: {rule['group']}, 关键词: {rule['keyword']}, "
                    f"发送词: {rule['send_word']}\n")
            self.group_info_text.insert(tk.END, 
                f"\n反馈QQ号: {data['FeedBackqq']}\n")
            
            # 更新关键词信息显示
            # self.keyword_info_text.delete(1.0, tk.END)
            # self.keyword_info_text.insert(tk.END, "目前检测的所有关键词:\n")
            # keywords = [rule['keyword'] for rule in data['checks']]
            # self.keyword_info_text.insert(tk.END, ', '.join(set(keywords)))
        
    def start_bot(self):
        data = self.load_data()
        start_date = data.get('start_date')
        if not start_date:
            start_date = datetime.datetime.now().strftime('%Y-%m-%d')
            data['start_date'] = start_date
            self.save_data(data)
        else:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            if (datetime.datetime.now() - start_date).days >= 31:
                messagebox.showinfo("更新提示", "该程序需要更新，请联系qq:2900153778，获取新版程序")
                return

        if not self.is_running:  # 检查是否已经有一个线程在运行
            try:
                self.bot_thread = BotThread()
                self.bot_thread.start()
            except Exception as e:
                messagebox.showerror("启动失败", f"无法启动机器人: {e}")
                self.start_button["text"] = "开始抢活！"
                self.start_button.config(state='normal')  # 启用“开始抢活！”按钮
                return
            self.start_button["text"] = "正在运行中..."
            self.start_button.config(state='disabled')  # 禁用“开始抢活！”按钮
            messagebox.showinfo("启动成功", "机器人已启动")
            self.status_text.insert(tk.END, "机器人已启动\n")
            self.load_data()  # 更新文本框的内容
            self.is_running = True  # 当程序运行时，设置标志位为True

    def stop_bot(self):
        if self.is_running:
            def stop_and_update():
                self.bot_thread.stop()
                while not self.bot_thread.stopped.is_set():  # 等待线程停止
                    time.sleep(0.1)
                messagebox.showerror("以点击停止", "这是一个浪费时间的弹窗，主要是防止线程阻塞，线程管理就是一坨大便（T_T）呜呜呜")
                if self.bot_thread.stopped.is_set():  # 检查进程是否已经停止
                    self.start_button["text"] = "开始抢活！"
                    self.start_button.config(state='normal')  # 启用“开始抢活！”按钮
                    messagebox.showinfo("停止成功", "机器人已停止")
                    self.status_text.insert(tk.END, "机器人已停止\n")
                    self.is_running = False  # 当程序停止运行时，设置标志位为False
                else:
                    messagebox.showerror("停止失败", "机器人未能成功停止")

            # 使用一个新的线程来停止进程并更新UI
            threading.Thread(target=stop_and_update).start()
        else:
            messagebox.showinfo("停止失败", "机器人已经停止")

    def save_data(self, data):
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

def main():
    root = tk.Tk()  # 创建一个窗口
    root.title("自动抢活神器v2.0.0 design by colored-glaze") # 设置窗口标题
    app = Application(master=root)  # 创建一个应用程序
    app.mainloop()

if __name__ == "__main__":
    main()