from llm_client import call_deepseek

def build_summary_prompt(contents: list[str]) -> str:
    cleaned_contents = []

    for content in contents:
        cleaned_content = content.strip()

        if cleaned_content:
            cleaned_contents.append(cleaned_content)

    if not cleaned_contents:
        raise ValueError("学习记录不能为空")

    num_lines = []

    for index,content in enumerate(cleaned_contents, start=1):
        num_lines.append(f"{index}. {content}")

    records_text = "\n".join(num_lines)

    prompt = f"""
            你是一名懂得规划的python ai agent学习辅导专家也是职业指导与规划专家,
            用户的学习记录:
            {records_text}
            
            你需要根据用户的学习记录创建一个学习总结,并且判断目前的学习进度;
            要求提出三条下一步建议,并给出建议的详细描述;
            请用中文回答,确保你的回答完整,准确,有逻辑,不允许虚构没有提供的信息.
    """
    return prompt

def generate_summary(contents: list[str]) -> str:
    prompt = build_summary_prompt(contents)
    summary = call_deepseek(prompt)
    return summary