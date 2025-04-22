#!/bin/bash
while true; do
    scrapy crawl walm
    echo "Spider exited, waiting 5 minutes..."
    sleep 300
done