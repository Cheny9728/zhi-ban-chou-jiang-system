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
            pil_image = pil_image.resize((180, 30), Image.Resampling.LANCZOS)
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
        
        # 添加抽奖轮次计数器
        self.draw_count = 0
        
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
        
        # 重置按钮
        self.reset_btn = ttk.Button(
            self.control_frame,
            text="重置信息",
            command=self.confirm_reset,
            width=20
        )
        self.reset_btn.pack(pady=5, padx=10)
        
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
        
        # 添加清除历史按钮
        self.clear_history_btn = ttk.Button(
            self.control_frame,
            text="清除历史",
            command=self.confirm_clear_history,
            width=20
        )
        self.clear_history_btn.pack(pady=5)
        
        # 在左侧添加往年值班人员显示区域
        self.previous_duty_frame = ttk.LabelFrame(
            self.control_frame, 
            text="往年值班人员",
            padding=(5, 5, 5, 5)
        )
        self.previous_duty_frame.pack(fill='x', pady=10, padx=5)
        
        # 创建往年值班人员的文本显示框
        self.previous_duty_text = tk.Text(
            self.previous_duty_frame,
            height=6,
            width=25,
            wrap=tk.WORD,
            font=('微软雅黑', 9)
        )
        self.previous_duty_text.pack(fill='both', expand=True)
        self.previous_duty_text.config(state='disabled')
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(
            self.previous_duty_frame,
            orient='vertical',
            command=self.previous_duty_text.yview
        )
        scrollbar.pack(side='right', fill='y')
        self.previous_duty_text.config(yscrollcommand=scrollbar.set)
        
        # 在抽奖设置区域添加选择框
        settings_frame = ttk.LabelFrame(
            self.control_frame,
            text="抽奖设置",
            padding=(5, 5, 5, 5)
        )
        settings_frame.pack(fill='x', padx=5, pady=5)
        
        # 添加往年值班人员参与选择
        self.include_previous = tk.BooleanVar(value=False)
        self.include_previous_check = ttk.Checkbutton(
            settings_frame,
            text="允许往年值班人员参与",
            variable=self.include_previous
        )
        self.include_previous_check.pack(anchor='w', padx=5, pady=2)
        
        # 右侧区分为三部分
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
        # 用英文作为列标识符
        columns = ('number', 'name', 'position')
        self.candidate_tree = ttk.Treeview(
            self.candidate_frame,
            columns=columns,
            show='headings',
            height=5,
            style='Candidate.Treeview'
        )
        
        # 设置列宽和对齐方式
        self.candidate_tree.column('number', width=80, anchor='center')
        self.candidate_tree.column('name', width=120, anchor='center')
        self.candidate_tree.column('position', width=100, anchor='center')
        
        # 设置表头显示文本
        self.candidate_tree.heading('number', text='序号')
        self.candidate_tree.heading('name', text='候选名单')
        self.candidate_tree.heading('position', text='职位')
        
        self.candidate_tree.pack(fill='x', padx=5, pady=5)
    
    def create_result_treeview(self):
        """创建结果表格"""
        # 创建滚动条
        scrollbar = ttk.Scrollbar(self.result_frame)
        scrollbar.pack(side='right', fill='y')
        
        # 使用英文作为列标识符
        columns = ('number', 'name', 'position', 'time')
        self.result_tree = ttk.Treeview(
            self.result_frame,
            columns=columns,
            show='headings',
            height=10,  # 设置为10行
            yscrollcommand=scrollbar.set,
            style='Result.Treeview'
        )
        
        # 设置列宽和对齐方式
        self.result_tree.column('number', width=80, anchor='center')
        self.result_tree.column('name', width=120, anchor='center')
        self.result_tree.column('position', width=100, anchor='center')
        self.result_tree.column('time', width=100, anchor='center')
        
        # 设置表头显示文本
        self.result_tree.heading('number', text='序号')
        self.result_tree.heading('name', text='中奖名单')
        self.result_tree.heading('position', text='职位')
        self.result_tree.heading('time', text='抽奖时间')
        
        # 绑定滚动条
        scrollbar.config(command=self.result_tree.yview)
        
        self.result_tree.pack(fill='both', expand=True, padx=5, pady=5)
    
    def import_file(self):
        """导入Excel文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_path:
            try:
                # 读取Excel文件，将空值转换为NaN
                df = pd.read_excel(file_path, keep_default_na=True)
                
                if len(df.columns) < 3:
                    raise ValueError("Excel文件必须包含姓名、职位和往年值班情况三列")
                
                # 清理数据
                df = df.fillna('')  # 将NaN���换为空字符串
                
                # 获取并清理数据
                self.names = [str(name).strip() for name in df.iloc[:, 0].tolist()]
                self.positions = [str(pos).strip() for pos in df.iloc[:, 1].tolist()]
                self.previous_duty = df.iloc[:, 2].tolist()  # 保存往年值班情况
                
                # 过滤掉空行
                valid_data = [
                    (name, pos, duty) for name, pos, duty in zip(self.names, self.positions, self.previous_duty)
                    if name and pos  # 确保姓名和职位不为空
                ]
                
                if not valid_data:
                    raise ValueError("文件中没有有效数据")
                
                # 更新有效数据
                self.names = [name for name, _, _ in valid_data]
                self.positions = [pos for _, pos, _ in valid_data]
                self.previous_duty = [duty for _, _, duty in valid_data]
                
                # 更新文件标签
                self.file_label.config(
                    text=f"已导入: {Path(file_path).name}\n共 {len(self.names)} 人"
                )
                
                # 显示往年值班人员
                self._show_previous_duty_members(valid_data)
                
                # 更新统计信息
                self.update_stats()
                
            except Exception as e:
                messagebox.showerror("错误", f"导入文件失败：{str(e)}")

    def _show_previous_duty_members(self, members_data):
        """显示往年值班人员"""
        try:
            # 启用文本框编辑
            self.previous_duty_text.config(state='normal')
            # 清空现有内容
            self.previous_duty_text.delete('1.0', tk.END)
            
            # 筛选并显示往年值班人员
            previous_duty_members = []
            for name, position, duty in members_data:
                # 跳过空值
                if pd.isna(name) or pd.isna(position) or pd.isna(duty):
                    continue
                    
                # 规范化duty的值并检查
                duty_str = str(duty).strip().lower()
                if duty_str in ['是', 'yes', '1', 'true', 'y']:
                    # 确保name和position都是字符串且去除首尾空格
                    name = str(name).strip()
                    position = str(position).strip()
                    if name and position:  # 确保都不为空
                        previous_duty_members.append(f"{name} ({position})")
            
            # 按姓名排序
            previous_duty_members.sort()
            
            if previous_duty_members:
                # 使用更清晰的格式显示
                header = "【往年值班人员】\n"
                content = "\n".join(f"• {member}" for member in previous_duty_members)
                self.previous_duty_text.insert('1.0', f"{header}\n{content}")
            else:
                self.previous_duty_text.insert('1.0', "暂无往年值班人员记录")
            
            # 禁用文本框编辑
            self.previous_duty_text.config(state='disabled')
            
        except Exception as e:
            print(f"显示往年值班人员时出错: {str(e)}")
            self.previous_duty_text.config(state='normal')
            self.previous_duty_text.delete('1.0', tk.END)
            self.previous_duty_text.insert('1.0', "显示往年值班人员出错")
            self.previous_duty_text.config(state='disabled')
    
    def update_stats(self):
        """更新统计信息"""
        total = len(self.names) if self.names else 0
        drawn = len(self.winners) if self.winners else 0
        self.stats_label.config(
            text=f"总人数: {total}  |  已抽取: {drawn}"
        )
    
    def _get_previous_duty_members(self):
        """获取往年值班人员列表"""
        previous_duty = []
        
        # 从原始数据中获取往年值班人员
        if hasattr(self, 'original_data'):
            previous_duty = self.original_data[
                self.original_data.iloc[:, 2] == '是'
            ].iloc[:, 0].tolist()
        
        # 添加固定排除人员
        previous_duty.extend(['陈益', '邱虎'])
        
        return previous_duty

    def draw_winners(self, num):
        """执行抽奖并返回获奖者列表"""
        try:
            # 获取往年值班人员列表
            previous_duty_members = []
            if not self.include_previous.get():  # 根据选择决定是否排除往年值班人员
                previous_duty_members = self._get_previous_duty_members()
            
            # 分别获取负责人和普通成员候选人（排除特定人员和可能的往年值班人员）
            excluded_names = set(['陈益', '邱虎'] + previous_duty_members)
            
            # 如果不包含往年值班人员，添加提示信息
            exclude_info = "特定人员" if self.include_previous.get() else "往年值班人员和特定人员"
            
            leader_candidates = [(name, pos) for name, pos in zip(self.names, self.positions)
                               if "负责人" in pos and name not in excluded_names]
            member_candidates = [(name, pos) for name, pos in zip(self.names, self.positions)
                               if "负责人" not in pos and name not in excluded_names]
            
            winners = []
            if self.required_leaders > 0:
                # 检查负责人数量是否足够
                if len(leader_candidates) < self.required_leaders:
                    raise ValueError(
                        f"负责人数量不足！需要{self.required_leaders}��，"
                        f"但只有{len(leader_candidates)}名负责人可用\n"
                        f"(已排除{exclude_info})"
                    )
                
                # 先抽取负责人
                selected_leaders = random.sample(leader_candidates, self.required_leaders)
                winners.extend([name for name, _ in selected_leaders])
                
                # 计算需要抽取的普通成员数量
                members_needed = num - self.required_leaders
                
                # 检查普通成员数量是否足够
                if len(member_candidates) < members_needed:
                    raise ValueError(
                        f"普通成员数量不足！需要{members_needed}人，"
                        f"但只有{len(member_candidates)}名成员可用\n"
                        f"(已排除{exclude_info})"
                    )
                
                # 抽取普通成员
                selected_members = random.sample(member_candidates, members_needed)
                winners.extend([name for name, _ in selected_members])
            else:
                # 不需要负责人时，从所有候选人中抽取
                all_candidates = leader_candidates + member_candidates
                if len(all_candidates) < num:
                    raise ValueError(
                        f"可用人数不足！需要{num}人，"
                        f"但只有{len(all_candidates)}人可用\n"
                        f"(已排除{exclude_info})"
                    )
                
                selected = random.sample(all_candidates, num)
                winners = [name for name, _ in selected]
            
            return winners
            
        except Exception as e:
            raise ValueError(f"抽取过程出错：{str(e)}")

    def start_lottery_animation(self):
        """开始抽奖动画"""
        if not self.names:
            messagebox.showwarning("警告", "请先导入名单！")
            return
            
        try:
            num = int(self.num_entry.get())
            self.required_leaders = int(self.leader_entry.get())
            
            if num <= 0:
                raise ValueError("抽奖人数必须大于0")
            if num > len(self.names):
                raise ValueError("抽奖人数不能大于总人数")
            if self.required_leaders < 0:
                raise ValueError("负责人数量不能为负数")
            if self.required_leaders > num:
                raise ValueError("负责人数量不能大于总抽奖人数")
            
            # 增加抽奖轮次计数
            self.draw_count += 1
            
            # 禁用抽奖按钮
            self.draw_btn.config(state='disabled')
            
            # 清空现有表格内容
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
            
            # 保存目标人数和动画次数
            self.target_num = num
            self.animation_count = 0
            self.max_animations = 20  # 设置动画循环次数
            
            # 先抽取最终结果
            self.winners = self.draw_winners(self.target_num)
            
            # 开始动画
            self.animate_lottery()
            
        except ValueError as e:
            messagebox.showerror("错误", str(e))
            self.draw_btn.config(state='normal')

    def animate_lottery(self):
        """执行抽奖动画"""
        try:
            # 清空候选人表格
            for item in self.candidate_tree.get_children():
                self.candidate_tree.delete(item)
            
            # 检查是否继续动画
            if self.animation_count < self.max_animations:
                # 创建动画效果 - 使用所有人员参与动画显示
                available_names = self.names.copy()
                
                if not self.include_previous.get():
                    previous_duty = self._get_previous_duty_members()
                    available_names = [name for name in available_names 
                                     if name not in previous_duty]
                
                # 显示随机候选人
                for i in range(5):  # 显示5个候选人
                    if available_names:
                        random_idx = random.randrange(len(available_names))
                        random_name = available_names[random_idx]
                        random_position = self.positions[self.names.index(random_name)]
                        
                        # 所有候选人使用相同的显示样式
                        item = self.candidate_tree.insert('', 'end', values=(
                            f"候选{i+1}",
                            random_name,
                            random_position
                        ))
                        self.candidate_tree.item(item, tags=('spinning',))
                        
                        # 同步显示在抽奖结果中（不显示特定人员）
                        if i == 0 and random_name not in ['陈益', '邱虎']:
                            self.update_temp_result(random_name, random_position)
                
                # 增加动画���数
                self.animation_count += 1
                
                # 设置下一次动画，动画间隔随计数增加而变长
                delay = min(100 + self.animation_count * 20, 500)  # 逐渐减慢，最大500ms
                self.window.after(delay, self.animate_lottery)
            else:
                # 动画结束，显示最终结果
                self._show_final_results()
                
        except Exception as e:
            messagebox.showerror("错误", f"动画执行失败：{str(e)}")
            self.draw_btn.config(state='normal')

    def update_temp_result(self, name, position):
        """更新临时抽奖结果"""
        # 清空结果表格
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 显示当前抽取的结果
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # 插入临时结果
        self.result_tree.insert('', 'end', values=(
            "抽取中",
            name,
            position,
            current_time
        ))

    def _show_final_results(self):
        """显示最终抽奖结果弹窗"""
        result_window = tk.Toplevel(self.window)
        result_window.title("抽奖结果")
        
        # 设置窗口大小和位��
        window_width = 400
        window_height = 500
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        result_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建滚动框架
        main_frame = ttk.Frame(result_window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 添加标题
        title_label = ttk.Label(
            main_frame,
            text="🎉 抽奖结果 🎉",
            font=('微软雅黑', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # 创建表格
        columns = ('number', 'name', 'position', 'role')
        result_tree = ttk.Treeview(
            main_frame,
            columns=columns,
            show='headings',
            height=len(self.winners)
        )
        
        # 设置列宽和对齐方式
        result_tree.column('number', width=60, anchor='center')
        result_tree.column('name', width=100, anchor='center')
        result_tree.column('position', width=100, anchor='center')
        result_tree.column('role', width=100, anchor='center')
        
        # 设置表头
        result_tree.heading('number', text='序号')
        result_tree.heading('name', text='姓名')
        result_tree.heading('position', text='职位')
        result_tree.heading('role', text='本次角色')
        
        # 插入数据
        for i, winner_name in enumerate(self.winners, 1):
            winner_idx = self.names.index(winner_name)
            winner_position = self.positions[winner_idx]
            
            # 确定角色
            role = "负责人" if i <= self.required_leaders else "成员"
            
            item = result_tree.insert('', 'end', values=(
                f"第{i}名",
                winner_name,
                winner_position,
                role
            ))
            
            # 为负责人添加特殊样式
            if role == "负责人":
                result_tree.tag_configure('leader', background='#FFE4E1')
                result_tree.item(item, tags=('leader',))
        
        result_tree.pack(fill='x', pady=(0, 20))
        
        # 添加统计信息
        stats_text = f"共抽取 {len(self.winners)} 人"
        if self.required_leaders > 0:
            stats_text += f"（其中负责人 {self.required_leaders} 人）"
        
        stats_label = ttk.Label(
            main_frame,
            text=stats_text,
            font=('微软雅黑', 10)
        )
        stats_label.pack(pady=(0, 20))
        
        # 添加确认按钮
        confirm_btn = ttk.Button(
            main_frame,
            text="确认",
            command=lambda: self._confirm_results(result_window),
            width=15
        )
        confirm_btn.pack()
        
        # 设置窗口模态
        result_window.transient(self.window)
        result_window.grab_set()
        self.window.wait_window(result_window)

    def _confirm_results(self, result_window):
        """确认结果并更新显示"""
        try:
            # 关闭结果窗口
            result_window.destroy()
            
            # 更新界面显示
            self.update_result_display()
            
            # 保存历史记录（只在确认后保存）
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for winner in self.winners:
                position = self.positions[self.names.index(winner)]
                self.history.append((self.draw_count, winner, position, current_time))
            
            # 更新统计信息
            self.update_stats()
            
            # 启用抽奖按钮
            self.draw_btn.config(state='normal')
            
        except Exception as e:
            messagebox.showerror("错误", f"确认结果时出错：{str(e)}")
            self.draw_btn.config(state='normal')

    def export_results(self):
        """导出结果"""
        if not self.winners and not self.history:
            messagebox.showwarning("警告", "没有可导出的结果！")
            return
        
        # 创建选择窗口
        choice_window = tk.Toplevel(self.window)
        choice_window.title("选择导出内容")
        
        # 设置窗口大小和位置
        window_width = 300
        window_height = 200
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        choice_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建主框架
        main_frame = ttk.Frame(choice_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # 添加标题标签
        title_label = ttk.Label(
            main_frame,
            text="请选择要导出的内容：",
            font=('微软雅黑', 10)
        )
        title_label.pack(pady=(0, 20))
        
        # 添加按钮
        if self.winners:
            current_btn = ttk.Button(
                main_frame,
                text="导出本次结果",
                command=lambda: self._export_current_results(choice_window),
                width=20
            )
            current_btn.pack(pady=5)
        
        if self.history:
            history_btn = ttk.Button(
                main_frame,
                text="导出历史记录",
                command=lambda: self._export_history(choice_window),
                width=20
            )
            history_btn.pack(pady=5)
        
        # 设置窗口模态
        choice_window.transient(self.window)
        choice_window.grab_set()
        self.window.wait_window(choice_window)

    def _export_current_results(self, choice_window):
        """导出本次抽奖结果"""
        if not self.winners:
            messagebox.showwarning("警告", "没有本次抽奖结果！")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile="抽奖结果_本次.xlsx"
        )
        
        if file_path:
            try:
                # 获取获奖者的职位信息
                winner_positions = [self.positions[self.names.index(name)] for name in self.winners]
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 创建数据框
                df = pd.DataFrame({
                    '序号': [f"第{i+1}名" for i in range(len(self.winners))],
                    '姓名': self.winners,
                    '职位': winner_positions,
                    '角色': ['负责人' if i < self.required_leaders else '成员' 
                           for i in range(len(self.winners))],
                    '抽奖时间': [current_time] * len(self.winners)
                })
                
                df.to_excel(file_path, index=False)
                messagebox.showinfo("成功", "本次结果已导出！")
                choice_window.destroy()
                
            except Exception as e:
                messagebox.showerror("错误", f"导出失败：{str(e)}")

    def _export_history(self, choice_window):
        """导出历史记录"""
        if not self.history:
            messagebox.showwarning("警告", "没有历史记录！")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile="抽奖结果_历史记录.xlsx"
        )
        
        if file_path:
            try:
                # 创建数据框
                data = []
                for round_num, name, position, time_str in self.history:
                    data.append({
                        '轮次': f"第{round_num}轮",
                        '姓名': name,
                        '职位': position,
                        '抽奖时间': time_str
                    })
                
                df = pd.DataFrame(data)
                df.to_excel(file_path, index=False)
                messagebox.showinfo("成功", "历史记录已导出！")
                choice_window.destroy()
                
            except Exception as e:
                messagebox.showerror("错误", f"导出失败：{str(e)}")
    
    def save_to_history(self):
        """保存抽奖结果到历史记录"""
        if self.winners:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for winner in self.winners:
                position = self.positions[self.names.index(winner)]
                # 保存轮次信息
                self.history.append((self.draw_count, winner, position, current_time))
    
    def show_history(self):
        """显示历史记录"""
        if not self.history:  # 只检查历史记录，不包括当前winners
            messagebox.showinfo("提示", "暂无抽奖历史记录")
            return
            
        # 创建历史记录窗口
        history_window = tk.Toplevel(self.window)
        history_window.title("抽奖历史记录")
        history_window.geometry("600x400")
        
        # 创建表格
        columns = ('round', 'number', 'name', 'position', 'time')
        history_tree = ttk.Treeview(
            history_window,
            columns=columns,
            show='headings',
            height=15
        )
        
        # 设置列
        history_tree.column('round', width=80, anchor='center')
        history_tree.column('number', width=80, anchor='center')
        history_tree.column('name', width=120, anchor='center')
        history_tree.column('position', width=120, anchor='center')
        history_tree.column('time', width=150, anchor='center')
        
        # 设置表头
        history_tree.heading('round', text='轮次')
        history_tree.heading('number', text='序号')
        history_tree.heading('name', text='中奖名单')
        history_tree.heading('position', text='职位')
        history_tree.heading('time', text='抽奖时间')
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(
            history_window,
            orient='vertical',
            command=history_tree.yview
        )
        scrollbar.pack(side='right', fill='y')
        history_tree.configure(yscrollcommand=scrollbar.set)
        
        # 按轮次分组记录
        grouped_records = {}
        for record in self.history:  # 只使用已保存的历史记录
            round_num, name, position, time_str = record
            if round_num not in grouped_records:
                grouped_records[round_num] = []
            grouped_records[round_num].append((name, position, time_str))
        
        # 显示分组后的记录
        for round_num in sorted(grouped_records.keys(), reverse=True):
            records = grouped_records[round_num]
            for i, (name, position, time_str) in enumerate(records, 1):
                history_tree.insert('', 'end', values=(
                    f"第{round_num}轮",
                    f"第{i}名",
                    name,
                    position,
                    time_str
                ))
        
        history_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 设置窗口模态
        history_window.transient(self.window)
        history_window.grab_set()
        self.window.wait_window(history_window)
    
    def confirm_reset(self):
        """确认重置"""
        if messagebox.askyesno("确认", "确定要重置所有信息吗？"):
            self.names = []
            self.positions = []
            self.winners = []
            self.draw_count = 0  # 重置抽奖次数
            self.file_label.config(text="未导入文件")
            self.update_stats()
            messagebox.showinfo("提示", "已重置所有信息")
    
    def confirm_clear_history(self):
        """确认是否清除历史记录"""
        result = messagebox.askyesno(
            "确认清除",
            "确定要清除所有抽奖历史记录吗？\n此操作不可恢复。",
            icon='warning'
        )
        
        if result:
            self.clear_history()

    def clear_history(self):
        """清除历史记录"""
        try:
            # 清除历史记录
            self.history = []
            self.winners = []  # 清除当前中奖记录
            
            # 更新界面
            # 1. 清空结果表格
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
            
            # 2. 更新统计信息
            self.update_stats()
            
            # 3. 确保按钮状态正确
            self.draw_btn.config(state='normal')
            
            # 显示清除成功消息
            messagebox.showinfo("成功", "历史记录已清除！")
            
        except Exception as e:
            messagebox.showerror("错误", f"清除历史记录时出错：{str(e)}")
    
    def update_result_display(self):
        """更新结果显示"""
        try:
            # 清空结果表格
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
            
            # 显示获奖结果
            current_time = datetime.now().strftime("%H:%M:%S")
            
            for i, winner_name in enumerate(self.winners, 1):
                winner_idx = self.names.index(winner_name)
                winner_position = self.positions[winner_idx]
                
                # 确定角色
                role = "负责人" if i <= self.required_leaders else "成员"
                
                # 插入结果
                item = self.result_tree.insert('', 'end', values=(
                    f"第{i}名",
                    winner_name,
                    winner_position,
                    current_time
                ))
                
                # 为负责人添加特殊样式
                if role == "负责人":
                    self.result_tree.tag_configure('leader', background='#FFE4E1')
                    self.result_tree.item(item, tags=('leader',))
                    
        except Exception as e:
            print(f"更新结果显示时出错: {str(e)}")
            messagebox.showerror("错误", f"更新结果显示失败：{str(e)}")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = LotterySystem()
    app.run()
