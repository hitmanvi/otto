import json
import csv
from pathlib import Path
import glob
import zipfile
import os
import shutil

def merge_to_csv():
    # 获取所有JSON文件
    data_dir = Path('seller_data')
    json_files = glob.glob(str(data_dir / 'seller_*.json'))
    
    if not json_files:
        print("No JSON files found in seller_data directory")
        return
    
    # 提取所有seller_id
    seller_ids = []
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                seller_ids.append(int(data['seller_id']))
        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
    
    if not seller_ids:
        print("No valid seller data found")
        return
    
    # 获取最小和最大的seller_id
    min_id = min(seller_ids)
    max_id = max(seller_ids)
    
    # 创建CSV文件名
    csv_filename = f'sellers_data/sellers_{min_id}_to_{max_id}.csv'
    
    # 定义CSV字段
    fieldnames = [
        'seller_id', 'name', 'address', 'phone', 
        'rating', 'items_count', 'ratings_count', 'reviews_count'
    ]
    
    # 写入CSV文件
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # 按seller_id排序处理文件
        for seller_id in sorted(seller_ids):
            file_path = data_dir / f'seller_{seller_id}.json'
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    writer.writerow(data)
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
    
    print(f"Successfully merged {len(seller_ids)} records into {csv_filename}")
    
    # 创建ZIP文件并添加所有JSON文件
    zip_filename = f'seller_data/seller_data_{min_id}_to_{max_id}.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in json_files:
            zipf.write(file_path, os.path.basename(file_path))
    
    print(f"Successfully compressed {len(json_files)} JSON files into {zip_filename}")
    
    # 删除原始JSON文件
    for file_path in json_files:
        os.remove(file_path)
    
    print(f"Deleted {len(json_files)} original JSON files")

if __name__ == "__main__":
    merge_to_csv() 