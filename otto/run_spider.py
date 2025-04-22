import subprocess
import time
import sys
from pathlib import Path
import os
import signal

def run_spider():
    # 切换到项目根目录
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # 设置全局变量来跟踪进程
    global process
    process = None
    
    # 处理终止信号
    def signal_handler(sig, frame):
        print("\nReceived termination signal. Cleaning up...")
        if process:
            try:
                process.terminate()
                process.wait(timeout=5)  # 给进程5秒钟来清理
            except subprocess.TimeoutExpired:
                process.kill()  # 如果进程没有及时终止，强制杀死
            print("Spider process terminated.")
        sys.exit(0)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    while True:
        try:
            print("Starting spider...")
            # 运行爬虫
            process = subprocess.Popen(
                ['scrapy', 'crawl', 'walm'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1  # 行缓冲，确保实时输出
            )
            
            # 实时输出爬虫日志
            stdout_thread = None
            stderr_thread = None
            
            # 使用非阻塞方式读取输出
            from threading import Thread
            
            def read_output(pipe, prefix):
                for line in pipe:
                    print(f"{prefix}: {line.strip()}")
            
            stdout_thread = Thread(target=read_output, args=(process.stdout, "STDOUT"))
            stderr_thread = Thread(target=read_output, args=(process.stderr, "STDERR"))
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()
            
            # 等待爬虫完成
            process.wait()
            
            # 等待输出线程完成
            if stdout_thread:
                stdout_thread.join(timeout=2)
            if stderr_thread:
                stderr_thread.join(timeout=2)
            
            # 检查退出状态
            if process.returncode != 0:
                print(f"Spider exited with error code {process.returncode}")
            
            print("Spider finished. Waiting 5 minutes before restarting...")
            process = None  # 清除进程引用
            time.sleep(300)  # 等待5分钟
            
        except KeyboardInterrupt:
            # 这里不需要处理，因为已经有信号处理器了
            pass
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            if process:
                try:
                    process.terminate()
                except:
                    pass
                process = None
            print("Waiting 5 minutes before restarting...")
            time.sleep(300)

if __name__ == "__main__":
    process = None  # 全局变量，用于跟踪爬虫进程
    run_spider()