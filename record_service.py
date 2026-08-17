import json
from pathlib import Path
from datetime import datetime
from uuid import uuid4

DATA_FILE = Path(__file__).with_name("history.json")

def create_record(content):
    #创建记录
    return {
        "id": str(uuid4()),  # 唯一标识符
        "content": content,  # 内容
        "completed": False,
        "created_at": datetime.now()
        .astimezone()
        .isoformat(timespec="seconds")  # 创建时间
    }

def save_history(history):
    #保存历史记录
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except OSError as error:
        print(f"保存历史记录文件时出错: {error}")
        return False

def normalize_history(history):
    #标准化历史记录
    normalized = []

    for item in history:
        if isinstance(item, str):
            normalized.append({
                "id": str(uuid4()),
                "content": item,
                "completed": False,
                "created_at": None
            })
        elif isinstance(item, dict):
            normalized_record = item.copy()
            normalized_record.setdefault("completed", False)  # 如果有completed字段，保留原值，否则添加completed并使用False
            normalized.append(normalized_record)

    return normalized

def load_history():
    #读取历史记录
    if not DATA_FILE.exists():
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except json.JSONDecodeError:
        print("历史记录文件格式错误，将使用空列表代替")
        return []
    except OSError as error:
        print(f"读取历史记录文件时出错: {error}")
        return []

    if not isinstance(history, list):
        print("历史记录的数据类型错误，将使用空列表代替")
        return []

    return normalize_history(history)

def add_record(history,content):
    #添加记录
    record = create_record(content)
    history.append(record)
    return record

def delete_record(history, num):
    #删除记录
    if num < 1 or num > len(history):
        return None

    index = num - 1
    return history.pop(index)

def update_record(history, num, new_content):
    #更新记录
    if num < 1 or num > len(history):
        return None

    index = num - 1
    record = history[index]

    record["content"] = new_content
    record["updated_at"] = (datetime.now()
                            .astimezone()
                            .isoformat(timespec="seconds")
    )

    return record

def clear_history(history):
    #清空历史记录
    history.clear()

def find_record_by_id(history,record_id):
    for record in history:
        if record.get("id") == record_id:
            return record
    return None

def delete_record_by_id(history,record_id):
    for index,record in enumerate(history): #因为我们需要真实列表索引，它本来就从0开始
        if record.get("id") == record_id:
            return history.pop(index)

    return None

def update_record_by_id(history,record_id,updates):
    record = find_record_by_id(history,record_id)

    if record is None:
        return None

    record.update(updates)  #

    record["updated_at"] = (
        datetime.now()
        .astimezone()
        .isoformat(timespec="seconds")
    )

    return record