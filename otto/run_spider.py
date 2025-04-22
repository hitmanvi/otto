import subprocess
import time
import sys
from pathlib import Path
import os

def run_spider():
    # 切换到项目根目录
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    while True:
        try:
            print("Starting spider...")
            # 运行爬虫
            process = subprocess.Popen(
                ['scrapy', 'crawl', 'walm'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # 实时输出爬虫日志
            for line in process.stdout:
                print(line.strip())
            
            # 等待爬虫完成
            process.wait()
            
            # 检查退出状态
            if process.returncode != 0:
                print(f"Spider exited with error code {process.returncode}")
                print("Error output:")
                for line in process.stderr:
                    print(line.strip())
            
            print("Spider finished. Waiting 5 minutes before restarting...")
            time.sleep(300)  # 等待5分钟
            
        except KeyboardInterrupt:
            print("\nStopping spider...")
            process.terminate()
            sys.exit(0)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Waiting 5 minutes before restarting...")
            time.sleep(300)

if __name__ == "__main__":
    run_spider() 