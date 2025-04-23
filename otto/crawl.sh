#!/bin/bash

# 获取参数
START_ID=${1:-101020000}
END_ID=${2:-101030000}
STEP=10000

current_start=$START_ID
current_end=$((current_start + STEP))

while [ $current_start -lt $END_ID ]; do
    # 确保不超过最大值
    if [ $current_end -gt $END_ID ]; then
        current_end=$END_ID
    fi
    
    echo "Starting crawl for range $current_start to $current_end"
    
    while true; do
        # 运行爬虫
        scrapy crawl walm -a start_id=$current_start -a end_id=$current_end
        
        # 检查完成标记文件
        COMPLETION_FILE="/var/www/html/crawl_data/walmart/completed_${current_start}_to_${current_end}.txt"
        
        if [ -f "$COMPLETION_FILE" ]; then
            echo "Crawling completed for range $current_start to $current_end"
            echo "Completion time: $(cat $COMPLETION_FILE)"
            break
        fi
        
        echo "Spider exited, waiting 5 minutes..."
        sleep 300
    done
    
    # 移动到下一个范围
    current_start=$current_end
    current_end=$((current_start + STEP))
done

echo "All ranges completed from $START_ID to $END_ID"