import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import yaml
import os
import sys
from tkinter import messagebox
from datetime import datetime

class ProxyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("节点转换工具 v1.0")
        self.root.geometry("800x700")
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加作者信息和版本信息框架
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # 作者信息使用更明显的样式
        author_label = tk.Label(
            info_frame, 
            text="作者: YouTube 科技共享", 
            font=('Microsoft YaHei', 10, 'bold'),  # 使用微软雅黑字体，加粗
            fg='#333333'  # 更深的颜色
        )
        author_label.pack(side=tk.LEFT, padx=(0, 20))  # 添加右边距
        
        # 版本信息
        version_label = tk.Label(
            info_frame,
            text="版本: v1.0",
            font=('Microsoft YaHei', 10),
            fg='#666666'
        )
        version_label.pack(side=tk.LEFT)
        
        # 添加分隔线
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 起始端口输入 (注意row值增加了1)
        port_frame = ttk.Frame(main_frame)
        port_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Label(port_frame, text="起始端口:").pack(side=tk.LEFT)
        self.start_port = tk.StringVar(value="42000")
        port_entry = ttk.Entry(port_frame, textvariable=self.start_port, width=10)
        port_entry.pack(side=tk.LEFT, padx=(5, 20))
        
        # 端口信息显示
        self.port_info = tk.StringVar(value="端口范围: 暂无")
        ttk.Label(port_frame, textvariable=self.port_info).pack(side=tk.LEFT)
        
        # 输入区域 (注意row值增加)
        ttk.Label(main_frame, text="输入节点配置:").grid(row=3, column=0, sticky=tk.W, pady=(10,0))
        self.input_text = scrolledtext.ScrolledText(main_frame, width=80, height=10)
        self.input_text.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        convert_btn = ttk.Button(button_frame, text="转换配置", command=self.convert_config)
        convert_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = ttk.Button(button_frame, text="保存配置文件", command=self.save_config)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # 节点统计信息
        self.node_count = tk.StringVar(value="节点数量: 0")
        ttk.Label(button_frame, textvariable=self.node_count).pack(side=tk.LEFT, padx=20)
        
        # 输出区域
        ttk.Label(main_frame, text="转换后的配置:").grid(row=6, column=0, sticky=tk.W)
        self.output_text = scrolledtext.ScrolledText(main_frame, width=80, height=15)
        self.output_text.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E))

    def convert_config(self):
        try:
            # 获取输入内容
            input_text = self.input_text.get("1.0", tk.END)
            start_port = int(self.start_port.get())
            
            # 解析输入的YAML
            input_config = yaml.safe_load(input_text)
            
            # 创建基础配置
            output_config = {
                'allow-lan': True,
                'dns': {
                    'enable': True,
                    'enhanced-mode': 'fake-ip',
                    'fake-ip-range': '198.18.0.1/16',
                    'default-nameserver': ['114.114.114.114'],
                    'nameserver': ['https://doh.pub/dns-query']
                },
                'listeners': [],
                'proxies': []
            }
            
            # 处理代理配置
            if isinstance(input_config, dict) and 'proxies' in input_config:
                proxies = input_config['proxies']
            else:
                proxies = input_config
                
            # 生成监听器和代理配置
            for i, proxy in enumerate(proxies):
                # 添加监听器配置
                listener = {
                    'name': f'mixed{i}',
                    'type': 'mixed',
                    'port': start_port + i,
                    'proxy': proxy['name']
                }
                output_config['listeners'].append(listener)
                
                # 添加代理配置
                output_config['proxies'].append(proxy)
            
            # 更新端口信息和节点数量
            end_port = start_port + len(proxies) - 1
            self.port_info.set(f"端口范围: {start_port} - {end_port}")
            self.node_count.set(f"节点数量: {len(proxies)}")
            
            # 转换为YAML并显示
            output_yaml = yaml.dump(output_config, allow_unicode=True, sort_keys=False)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", output_yaml)
            
            messagebox.showinfo("成功", f"配置转换完成！\n生成了 {len(proxies)} 个本地节点\n端口范围: {start_port}-{end_port}")
            
        except Exception as e:
            messagebox.showerror("错误", f"转换失败: {str(e)}")

    def save_config(self):
        try:
            if not self.output_text.get("1.0", tk.END).strip():
                messagebox.showwarning("警告", "没有可保存的配置！请先转换配置。")
                return
                
            # 生成默认文件名
            default_filename = f"clash_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
            
            # 打开文件保存对话框
            file_path = filedialog.asksaveasfilename(
                defaultextension=".yaml",
                filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.output_text.get("1.0", tk.END))
                messagebox.showinfo("成功", f"配置已保存到:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")

def resource_path(relative_path):
    """ 获取资源绝对路径 """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    root = tk.Tk()
    app = ProxyConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main() 