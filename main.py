import record_service as service

def show_history(history):
    #显示历史记录
    if not history:
        print("没有历史记录")
        return

    for index, record in enumerate(history, start=1):
        content = record["content"]
        completed = record.get("completed", False)
        status_text = "已完成" if completed else "未完成"
        created_at = record.get("created_at") or "时间未知"
        update_at = record.get("updated_at")
        if update_at:
            print(f"{index}. [{status_text}] [{created_at}]"
                  f"{content} (更新于{update_at})")
        else:
            print(f"{index}. [{status_text}] [{created_at}] {content}")



def main():
    #控制程序运行流程
    history = service.load_history()
    print("AI学习助手已启动,输入quit退出!")
    while True:
        user_input = input("请输入你的内容:").strip()
        if user_input == "quit":
            print("再见!")
            break
        elif user_input == "":
            print("输入不能为空")
        elif user_input == "history":
            show_history(history)
        elif user_input == "clear":
            service.clear_history(history)
            print("历史记录已清空")
            service.save_history(history)
        elif user_input == "delete":
            print("请输入要删除的记录编号,例如:delete 2")
        elif user_input.startswith("delete "):
            num_text = user_input.split(maxsplit=1)[1]

            try:
                num = int(num_text)
            except ValueError:
                print("输入无效，删除编号必须是整数")
                continue

            deleted_record = service.delete_record(history, num)

            if deleted_record is None:
                print("记录编号不存在")
            else:
                saved = service.save_history(history)
                content = deleted_record["content"]
                if saved:
                    print(f"已删除 {content} 并保存成功")
                else:
                    print(f"已删除 {content} 但保存到硬盘失败")
        elif user_input == "update" or  user_input.startswith("update "):
            part = user_input.split(maxsplit=2)
            if len(part) < 3:
                print("输入格式错误，请输入update 编号 新内容")
                continue

            command, num_text, new_content = part
            try:
                num = int(num_text)
            except ValueError:
                print("输入无效，编号必须是整数")
                continue

            updated_record = service.update_record(history, num, new_content)

            if updated_record is None:
                print("记录编号不存在")
                continue

            saved = service.save_history(history)
            if saved:
                print(f"已更新 {updated_record['content']} 并保存成功")
            else:
                print(f"已更新 {updated_record['content']} 但保存到硬盘失败")

        else:
            service.add_record(history, user_input)
            saved = service.save_history(history)
            if saved :
                index = len(history)
                print(f"记录并保存成功:{user_input} (编号:{index})")
            else:
                print(f"记录成功但保存到硬盘失败")

if __name__ == "__main__":
    main()