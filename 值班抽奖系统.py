import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import pandas as pd
import random
from pathlib import Path
import time
from datetime import datetime
import os
from PIL import Image, ImageTk
import base64
import sys

class LotterySystem:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("值班抽奖系统")
        self.window.geometry("900x700")  # 增加窗口大小以适应logo
        
        try:
            # 获取程序运行路径
            if getattr(sys, 'frozen', False):
                # 打包后的路径
                application_path = sys._MEIPASS
            else:
                # 开发环境路径
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            logo_path = os.path.join(application_path, 'Imgs', 'LOGO.png')
            # 使用PIL加载图片
            pil_image = Image.open(logo_path)
            # 调整大小
            pil_image = pil_image.resize((150, 30), Image.Resampling.LANCZOS)
            # 转换为PhotoImage
            self.logo_image = ImageTk.PhotoImage(pil_image)
        except Exception as e:
            print(f"Logo加载失败: {str(e)}")
            self.logo_image = None
        
        # 存储人员名单和中奖历史
        self.names = []
        self.positions = []
        self.history = []
        self.winners = []
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 左侧控制面板
        self.control_frame = ttk.LabelFrame(self.main_frame, text="控制面板")
        self.control_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        # 添加logo（如果加载成功）
        if self.logo_image:
            self.logo_label = ttk.Label(
                self.control_frame,
                image=self.logo_image
            )
            self.logo_label.pack(pady=10)
        
        # 导入文件按钮
        self.import_btn = ttk.Button(
            self.control_frame, 
            text="导入名单", 
            command=self.import_file,
            width=20
        )
        self.import_btn.pack(pady=10, padx=10)
        
        # 显示当前导入的文件
        self.file_label = ttk.Label(
            self.control_frame,
            text="未导入文件",
            wraplength=200
        )
        self.file_label.pack(pady=5)
        
        # 抽奖人数输入框
        self.num_frame = ttk.Frame(self.control_frame)
        self.num_frame.pack(pady=10)
        
        ttk.Label(self.num_frame, text="抽奖人数：").pack(side=tk.LEFT)
        self.num_entry = ttk.Entry(self.num_frame, width=10)
        self.num_entry.pack(side=tk.LEFT)
        self.num_entry.insert(0, "1")
        
        # 添加负责人数量输入框
        self.leader_frame = ttk.Frame(self.control_frame)
        self.leader_frame.pack(pady=10)
        
        ttk.Label(self.leader_frame, text="负责人数：").pack(side=tk.LEFT)
        self.leader_entry = ttk.Entry(self.leader_frame, width=10)
        self.leader_entry.pack(side=tk.LEFT)
        self.leader_entry.insert(0, "0")
        
        # 开始抽奖按钮
        self.draw_btn = ttk.Button(
            self.control_frame,
            text="开始抽奖",
            command=self.start_lottery_animation,
            width=20
        )
        self.draw_btn.pack(pady=10)
        
        # 导出结果按钮
        self.export_btn = ttk.Button(
            self.control_frame,
            text="导出结果",
            command=self.export_results,
            width=20
        )
        self.export_btn.pack(pady=10)
        
        # 查看历史按钮
        self.history_btn = ttk.Button(
            self.control_frame,
            text="查看历史",
            command=self.show_history,
            width=20
        )
        self.history_btn.pack(pady=10)
        
        # 右侧区域分为三部分
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # 上部分：抽奖统计信息
        self.stats_frame = ttk.LabelFrame(self.right_frame, text="抽奖统计")
        self.stats_frame.pack(fill='x', padx=5, pady=5)
        
        # 添加统计信息标签
        self.stats_label = ttk.Label(
            self.stats_frame,
            text="总人数: 0  |  已抽取: 0",
            font=('微软雅黑', 12)
        )
        self.stats_label.pack(pady=10)
        
        # 中部分：候选人转盘
        self.candidate_frame = ttk.LabelFrame(self.right_frame, text="抽奖转盘")
        self.candidate_frame.pack(fill='x', padx=5, pady=5)
        
        # 创建候选人表格
        self.create_candidate_treeview()
        
        # 下部分：抽奖结果
        self.result_frame = ttk.LabelFrame(self.right_frame, text="抽奖结果")
        self.result_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 创建结果表格
        self.create_result_treeview()
        
    def create_candidate_treeview(self):
        """创建候选人转盘表格"""
        columns = ('序号', '姓名', '职位')
        self.candidate_tree = ttk.Treeview(
            self.candidate_frame,
            columns=columns,
            show='headings',
            height=5,
            style='Candidate.Treeview'
        )
        
        # 设置列宽和对齐方式
        self.candidate_tree.column('序号', width=80, anchor='center')
        self.candidate_tree.column('姓名', width=120, anchor='center')
        self.candidate_tree.column('职位', width=100, anchor='center')
        
        # 设置表头
        self.candidate_tree.heading('序号', text='序号')
        self.candidate_tree.heading('姓名', text='候选名单')
        self.candidate_tree.heading('职位', text='职位')
        
        self.candidate_tree.pack(fill='x', padx=5, pady=5)
    
    def create_result_treeview(self):
        """创建结果表格"""
        # 创建滚动条
        scrollbar = ttk.Scrollbar(self.result_frame)
        scrollbar.pack(side='right', fill='y')
        
        columns = ('序号', '姓名', '职位', '时间')
        self.result_tree = ttk.Treeview(
            self.result_frame,
            columns=columns,
            show='headings',
            height=10,
            yscrollcommand=scrollbar.set,
            style='Result.Treeview'
        )
        
        # 设置列宽和对齐方式
        self.result_tree.column('序号', width=80, anchor='center')
        self.result_tree.column('姓名', width=120, anchor='center')
        self.result_tree.column('职位', width=100, anchor='center')
        self.result_tree.column('时间', width=100, anchor='center')
        
        # 设置表头
        self.result_tree.heading('序号', text='序号')
        self.result_tree.heading('姓名', text='中奖名单')
        self.result_tree.heading('职位', text='职位')
        self.result_tree.heading('时间', text='抽奖时间')
        
        # 绑定滚动条
        scrollbar.config(command=self.result_tree.yview)
        
        self.result_tree.pack(fill='both', expand=True, padx=5, pady=5)
    
    def import_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_path:
            try:
                df = pd.read_excel(file_path)
                if len(df.columns) < 2:
                    raise ValueError("Excel文件必须包含姓名和职位两列")
                    
                self.names = df.iloc[:, 0].tolist()  # 第一列为姓名
                self.positions = df.iloc[:, 1].tolist()  # 第二列为职位
                self.file_label.config(
                    text=f"已导入: {Path(file_path).name}\n共 {len(self.names)} 人"
                )
                # 更新统计信息
                self.update_stats()
            except Exception as e:
                messagebox.showerror("错误", f"导入文件失败：{str(e)}")
    
    def update_stats(self):
        """更新统计信息"""
        total = len(self.names) if self.names else 0
        drawn = len(self.winners) if self.winners else 0
        self.stats_label.config(
            text=f"总人数: {total}  |  已抽取: {drawn}"
        )
    
    def start_lottery_animation(self):
        if not self.names:
            messagebox.showwarning("警告", "请先导入名单！")
            return
            
        try:
            num = int(self.num_entry.get())
            if num <= 0:
                raise ValueError("抽奖人数必须大于0")
            if num > len(self.names):
                raise ValueError("抽奖人数不能大于总人数")
            
            required_leaders = int(self.leader_entry.get())
            if required_leaders < 0:
                raise ValueError("负责人数量不能为负数")
            if required_leaders > num:
                raise ValueError("负责人数量不能大于总抽奖人数")
            
            # 禁用按钮
            self.draw_btn.config(state='disabled')
            
            # 清空现有表格内容
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
            
            # 开始抽奖，考虑职位要求
            self.winners = self.draw_with_position_requirements(num)
            self.current_index = 0
            self.animate_lottery()
            
        except ValueError as e:
            messagebox.showerror("错误", str(e))
    
    def draw_with_position_requirements(self, num):
        """根据人数要求抽取指定数量的负责人和普通成员"""
        # 定义不参与抽取的人员名单
        excluded_names = ['陈益', '邱虎']
        
        # 获取还未中奖且在排除名单中的人员列表
        remaining_leaders = []
        remaining_others = []
        for i, name in enumerate(self.names):
            if name not in self.winners and name not in excluded_names:
                if self.positions[i] == "负责人":
                    remaining_leaders.append(i)
                else:
                    remaining_others.append(i)
        
        winners = []
        
        # 从输入框获取需要的负责人数量
        try:
            required_leaders = int(self.leader_entry.get())
            if required_leaders < 0:
                raise ValueError("负责人数量不能为负数")
            if required_leaders > num:
                raise ValueError("负责人数量不能大于总抽奖人数")
        except ValueError as e:
            if str(e).startswith("invalid literal"):
                raise ValueError("请输入有效的负责人数量")
            raise e
        
        # 检查是否有足够的负责人可供抽取
        if len(remaining_leaders) < required_leaders:
            raise ValueError(
                f"没有足够的负责人可供抽取\n"
                f"需要{required_leaders}名负责人，但只有{len(remaining_leaders)}名可用"
            )
        
        # 检查是否有足够的非负责人可供抽取
        needed_others = num - required_leaders
        if len(remaining_others) < needed_others:
            raise ValueError(
                f"没有足够的非负责人可供抽取\n"
                f"需要{needed_others}名非负责人，但只有{len(remaining_others)}名可用"
            )
        
        # 1. 先抽取指定数量的负责人
        if required_leaders > 0:
            selected_leaders = random.sample(remaining_leaders, required_leaders)
            for idx in selected_leaders:
                winners.append(self.names[idx])
        
        # 2. 再抽取剩余数量的非负责人
        if needed_others > 0:
            selected_others = random.sample(remaining_others, needed_others)
            for idx in selected_others:
                winners.append(self.names[idx])
        
        return winners
    
    def animate_lottery(self):
        if self.current_index < len(self.winners):
            # 动画效果：随机显示更多次数，制造转盘效果
            if self.current_index == len(self.winners) - 1:
                times = 20  # 最后一个名字显示更多次
            else:
                times = 15
            
            self.animate_single_winner(self.current_index, times)
        else:
            # 动画结束，启用按钮
            self.draw_btn.config(state='normal')
            # 保存历史记录
            self.save_to_history()
            # 更新统计信息
            self.update_stats()
    
    def animate_single_winner(self, index, remaining_times):
        if remaining_times > 0:
            # 清空候选人表格
            for item in self.candidate_tree.get_children():
                self.candidate_tree.delete(item)
            
            # 计算动画速度（逐渐减慢）
            delay = int(100 * (1 + (10 - remaining_times) * 0.3))
            
            # 转盘效果：同时显示多个名字
            displayed_names = []
            for i in range(5):  # 显示5个名字
                random_idx = random.randrange(len(self.names))
                random_name = self.names[random_idx]
                random_position = self.positions[random_idx]
                
                # 确保不显示被排除的名字和已中奖的人
                excluded_names = ['陈益', '邱虎'] + self.winners
                while random_name in excluded_names:
                    random_idx = random.randrange(len(self.names))
                    random_name = self.names[random_idx]
                    random_position = self.positions[random_idx]
                
                displayed_names.append((random_name, random_position))
            
            # 在转盘中显示候选人
            for i, (name, position) in enumerate(displayed_names):
                item = self.candidate_tree.insert('', i, values=(
                    f"候选{i+1}",
                    name,
                    position
                ))
                # 设置候选项样式
                self.candidate_tree.item(item, tags=('spinning',))
            
            # 设置渐变的动画间隔
            self.window.after(delay, lambda: self.animate_single_winner(
                index, remaining_times - 1))
        else:
            # 清空候选人表格
            for item in self.candidate_tree.get_children():
                self.candidate_tree.delete(item)
            
            # 在结果表格中显示新的中奖者
            winner_name = self.winners[index]
            winner_idx = self.names.index(winner_name)
            winner_position = self.positions[winner_idx]
            
            item = self.result_tree.insert('', 'end', values=(
                f"第{index+1}名",
                winner_name,
                winner_position,
                datetime.now().strftime("%H:%M:%S")
            ))
            # 设置获奖者样式
            self.result_tree.item(item, tags=('winner',))
            
            # 添加闪烁效果
            self.blink_winner(item, 5)  # 闪烁5次
            
            self.current_index += 1
            self.window.after(500, self.animate_lottery)
    
    def blink_winner(self, item, times):
        """为获奖项添加闪烁效果"""
        if times > 0:
            # 切换标签
            current_tags = self.result_tree.item(item)['tags']
            if 'winner' in current_tags:
                self.result_tree.item(item, tags=('candidate',))
            else:
                self.result_tree.item(item, tags=('winner',))
            
            # 继续闪烁
            self.window.after(300, lambda: self.blink_winner(item, times - 1))
        else:
            # 最终设置为获奖样式
            self.result_tree.item(item, tags=('winner',))
    
    def export_results(self):
        if not self.winners:
            messagebox.showwarning("警告", "还没有抽奖结果！")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        
        if file_path:
            try:
                # 获取获奖者的职位信息
                winner_positions = [self.positions[self.names.index(name)] for name in self.winners]
                
                df = pd.DataFrame({
                    '序号': [f"第{i+1}名" for i in range(len(self.winners))],
                    '姓名': self.winners,
                    '职位': winner_positions,
                    '时间': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * len(self.winners)
                })
                df.to_excel(file_path, index=False)
                messagebox.showinfo("成功", "结果已导出！")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败：{str(e)}")
    
    def save_to_history(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({
            'time': current_time,
            'winners': self.winners.copy()
        })
    
    def show_history(self):
        if not self.history:
            messagebox.showinfo("提示", "暂无历史记录")
            return
            
        history_window = tk.Toplevel(self.window)
        history_window.title("历史记录")
        history_window.geometry("600x400")
        
        # 创建历史记录表格
        columns = ('时间', '中奖名单')
        tree = ttk.Treeview(
            history_window,
            columns=columns,
            show='headings',
            height=15
        )
        
        tree.column('时间', width=200, anchor='center')
        tree.column('中奖名单', width=400, anchor='w')
        
        tree.heading('时间', text='抽奖时间')
        tree.heading('中奖名单', text='中奖名单')
        
        for record in self.history:
            tree.insert('', 'end', values=(
                record['time'],
                ', '.join(record['winners'])
            ))
            
        tree.pack(fill='both', expand=True, padx=10, pady=10)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = LotterySystem()
    app.run()
