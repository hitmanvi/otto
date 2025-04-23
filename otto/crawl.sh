#!/bin/bash
while true; do
    scrapy crawl walm -a start_id=101010000 -a end_id=101020000
    echo "Spider exited, waiting 5 minutes..."
    sleep 300
done