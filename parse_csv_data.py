import csv
import json

def parse_csv_to_markdown():
    """将CSV数据解析并转换为markdown格式"""
    
    # 读取CSV文件
    with open('/Users/edy/Desktop/project/挑战玩法/好人坏人挑战数据.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    # 解析每条数据
    cases = []
    for row in data:  # 处理所有数据
        pipe_id = row['pipe_id']
        try:
            content = json.loads(row['content'])
            in_param = json.loads(row['in_param'])
        except:
            continue
        
        # 提取背景介绍
        background = ""
        title = ""
        for item in content:
            if 'content' in item:
                for c in item['content']:
                    if c.get('val') == '背景介绍':
                        title = "背景介绍"
                        continue
                    if 'val' in c and c['val'] and c['val'] not in ['无', '应该', '先虐后虐', '三哥喜欢我', '我喜欢爸爸。', '在床上。']:
                        background = c['val']
                        break
        
        # 提取更多信息
        case_info = {
            'pipe_id': pipe_id,
            'background': background,
            'title': title
        }
        
        # 解析in_param中的模板信息
        for param in in_param:
            if 'val' in param and isinstance(param['val'], str):
                # 查找包含中文文本的system prompt
                if '你是{{system_1}}' in param['val']:
                    case_info['system_prompt'] = param['val']
                # 查找模型信息
                elif param.get('inName') == 'model':
                    case_info['model'] = param['val']
        
        if background:  # 只保留有背景介绍的案例
            cases.append(case_info)
    
    # 生成markdown
    with open('/Users/edy/Desktop/project/挑战玩法/好人坏人挑战优秀案例.md', 'w', encoding='utf-8') as f:
        f.write("# 10回合判断好坏人挑战优秀案例\n\n")
        f.write("本文档收录了判断类挑战的优秀案例，供参考学习。\n\n")
        
        valid_case_num = 1
        for case in cases:
            f.write(f"## 案例{valid_case_num}\n\n")
            f.write(f"**管道ID**: `{case['pipe_id']}`\n\n")
            
            if case.get('background'):
                # 格式化背景介绍
                bg = case['background'].replace('\\n', '\n')
                f.write(f"### 背景介绍\n\n{bg}\n\n")
            
            if case.get('model'):
                f.write(f"**使用模型**: {case['model']}\n\n")
            
            # 分析设计特点
            f.write("### 设计特点\n\n")
            bg = case.get('background', '')
            
            # 判断要求
            if '请判断' in bg:
                f.write("- **明确判断要求**：直接提出判断任务\n")
            if '好人？还是坏人？' in bg:
                f.write("- **标准二选一**：使用经典的好坏人判断格式\n")
                
            # 角色关系设置
            if '死对头' in bg:
                f.write("- **敌对关系**：设置商业死对头的对立关系\n")
            if '怪盗' in bg:
                f.write("- **神秘角色**：怪盗身份增加判断难度\n")
            if '黑猫' in bg and '说话' in bg:
                f.write("- **超自然元素**：会说话的黑猫增加神秘感\n")
                
            # 情境设计
            if '月圆之夜' in bg or '深夜' in bg:
                f.write("- **氛围营造**：夜晚场景增加紧张感\n")
            if '悬崖' in bg or '受伤' in bg:
                f.write("- **危机情境**：危险处境考验判断\n")
                
            # 心理设计
            if '却也没伤害过你' in bg:
                f.write("- **矛盾线索**：'死对头却没伤害过'制造迷惑\n")
            if '好奇心' in bg:
                f.write("- **心理驱动**：利用玩家好奇心推进剧情\n")
            if '对你示好' in bg or '想和你合作' in bg:
                f.write("- **行为反常**：突然的态度转变引发疑问\n")
            if '两个结局都是判断成功' in bg:
                f.write("- **特殊设计**：打破常规的双成功结局\n")
            
            f.write("\n---\n\n")
            valid_case_num += 1

if __name__ == "__main__":
    parse_csv_to_markdown()
    print("解析完成！已生成 好人坏人挑战优秀案例.md")