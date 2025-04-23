#!/bin/bash
# Loop through the range from 101020000 to 101100000 with step 10000
for ((start_id=101020000; start_id<101100000; start_id+=10000)); do
    end_id=$((start_id+10000))
    echo "Starting crawl from $start_id to $end_id"
    
    scrapy crawl walm -a start_id=$start_id -a end_id=$end_id
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "Spider completed successfully for range $start_id to $end_id"
    else
        echo "Spider exited with error code $exit_code for range $start_id to $end_id, waiting 5 minutes..."
        sleep 300
        # Retry the current range
        start_id=$((start_id-10000))
    fi
done

echo "All crawling tasks completed"