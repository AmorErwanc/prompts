import csv
import json

def parse_csv_to_markdown():
    """将CSV数据解析并转换为markdown格式，提取完整的模板变量内容"""
    
    # 读取CSV文件
    with open('/Users/edy/Desktop/project/挑战玩法/好人坏人挑战数据.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    # 解析每条数据
    cases = []
    for row in data:
        pipe_id = row['pipe_id']
        try:
            content = json.loads(row['content'])
            in_param = json.loads(row['in_param'])
        except:
            continue
        
        case_info = {
            'pipe_id': pipe_id,
            'attrs': {}  # 存储所有属性
        }
        
        # 解析content部分获取背景介绍
        for item in content:
            if 'content' in item:
                for c in item['content']:
                    if c.get('val') == '背景介绍':
                        continue
                    if 'val' in c and c['val'] and c['val'] not in ['无', '应该', '先虐后虐', '三哥喜欢我', '我喜欢爸爸。', '在床上。']:
                        case_info['背景介绍'] = c['val']
                        if 'outName' in c:
                            case_info['attrs']['背景介绍_id'] = c['outName']
        
        # 解析in_param部分
        role_id = None
        inner_personality_id = None
        opening_id = None
        
        for param in in_param:
            # 查找角色相关的ID
            if 'outName' in param and 'val' in param:
                out_name = param['outName']
                val = param['val']
                
                # 根据命名模式识别不同的ID
                if param.get('inName', '').startswith('system_1'):
                    role_id = val
                elif param.get('inName', '').startswith('system_4'):
                    inner_personality_id = val
                elif param.get('inName', '').startswith('initChat_2'):
                    opening_id = val
                elif param.get('inName') == 'model':
                    case_info['模型'] = val
        
        # 保存ID信息
        if role_id:
            case_info['attrs']['角色ID'] = role_id
        if inner_personality_id:
            case_info['attrs']['内在人设ID'] = inner_personality_id
        if opening_id:
            case_info['attrs']['开场白ID'] = opening_id
        
        # 只保留有背景介绍的案例
        if '背景介绍' in case_info:
            cases.append(case_info)
    
    # 生成markdown
    with open('/Users/edy/Desktop/project/挑战玩法/好人坏人挑战优秀案例.md', 'w', encoding='utf-8') as f:
        f.write("# 10回合判断好坏人挑战优秀案例\n\n")
        f.write("本文档收录了判断类挑战模板的完整变量内容。\n\n")
        
        for i, case in enumerate(cases, 1):
            f.write(f"## 案例{i}\n\n")
            f.write(f"**管道ID**: `{case['pipe_id']}`\n\n")
            
            # 输出背景介绍
            if '背景介绍' in case:
                bg = case['背景介绍'].replace('\\n', '\n')
                f.write(f"### 背景介绍\n```\n{bg}\n```\n\n")
            
            # 输出属性ID信息（这些ID对应实际的内容）
            if case['attrs']:
                f.write("### 相关变量ID\n")
                for key, value in case['attrs'].items():
                    f.write(f"- **{key}**: `{value}`\n")
                f.write("\n")
            
            # 输出模型信息
            if '模型' in case:
                f.write(f"### 使用模型\n`{case['模型']}`\n\n")
            
            # 注意事项
            f.write("### 模板变量说明\n")
            f.write("由于数据结构限制，以下变量内容需要通过对应ID在系统中查询：\n")
            f.write("- **内在人设**: 通过`内在人设ID`查询\n")
            f.write("- **开场白**: 通过`开场白ID`查询\n")
            f.write("- **好人结局**: 需要在完整模板中查看\n")
            f.write("- **坏人结局**: 需要在完整模板中查看\n")
            f.write("- **角色基本信息**: 通过`角色ID`查询（包含姓名、性别、设定）\n")
            
            f.write("\n---\n\n")

if __name__ == "__main__":
    parse_csv_to_markdown()
    print("解析完成！已生成 好人坏人挑战优秀案例.md")