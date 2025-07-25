import csv
import json

def full_parse_csv():
    """完整解析CSV数据结构，提取所有模板变量"""
    
    # 读取CSV文件
    with open('/Users/edy/Desktop/project/挑战玩法/好人坏人挑战数据.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    # 选择顾飞祁案例
    target_row = None
    for row in data:
        if '顾飞祁' in row.get('content', ''):
            target_row = row
            break
    
    if not target_row:
        return
    
    # 解析in_param
    in_param = json.loads(target_row['in_param'])
    
    # 查找包含set数组的参数
    for param in in_param:
        if 'set' in param and isinstance(param['set'], list):
            print("找到set数组，包含以下内容：")
            print("-" * 50)
            
            for idx, item in enumerate(param['set']):
                print(f"\n项目{idx+1}:")
                print(f"  inName: {item.get('inName')}")
                print(f"  outName: {item.get('outName')}")
                print(f"  chainId: {item.get('chainId')}")
                if 'val' in item:
                    if isinstance(item['val'], str):
                        if len(item['val']) > 200:
                            print(f"  val: {item['val'][:200]}...")
                        else:
                            print(f"  val: {item['val']}")
                            
    # 生成最终的markdown文档
    print("\n\n=== 提取的模板变量 ===")
    
    # 从content中提取背景介绍
    content = json.loads(target_row['content'])
    background = ""
    for item in content:
        if 'content' in item:
            for c in item['content']:
                if c.get('val') and '顾飞祁' in c.get('val', ''):
                    background = c['val']
                    
    # 查找各种ID
    role_id = ""
    inner_id = ""
    opening_id = ""
    model = ""
    system_prompt = ""
    
    for param in in_param:
        if 'set' in param and isinstance(param['set'], list):
            for item in param['set']:
                if item.get('inName') == 'system_1':
                    role_id = item.get('val', '')
                elif item.get('inName') == 'system_4':
                    inner_id = item.get('val', '')
                elif item.get('inName') == 'model':
                    model = item.get('val', '')
                elif item.get('inName') == 'system' and 'val' in item:
                    system_prompt = item['val']
                    
        if param.get('inName') == 'initChat_2':
            opening_id = param.get('val', '')
    
    # 生成markdown
    with open('/Users/edy/Desktop/project/挑战玩法/顾飞祁案例完整解析.md', 'w', encoding='utf-8') as f:
        f.write("# 顾飞祁案例完整解析\n\n")
        f.write("## 提取的变量信息\n\n")
        
        f.write(f"### 背景介绍\n```\n{background}\n```\n\n")
        
        f.write("### ID信息\n")
        f.write(f"- 角色ID: `{role_id}`\n")
        f.write(f"- 内在人设ID: `{inner_id}`\n")
        f.write(f"- 开场白ID: `{opening_id}`\n")
        f.write(f"- 使用模型: `{model}`\n\n")
        
        if system_prompt:
            f.write("### 系统提示词模板\n```\n")
            f.write(system_prompt)
            f.write("\n```\n\n")
            
        f.write("## 数据结构说明\n\n")
        f.write("CSV中的数据采用了ID引用机制：\n")
        f.write("1. **角色基本信息**（姓名、性别、设定）通过`角色ID`引用\n")
        f.write("2. **内在人设**通过`内在人设ID`引用\n")
        f.write("3. **开场白**通过`开场白ID`引用\n")
        f.write("4. **好人结局**和**坏人结局**未在CSV中直接存储，需要在完整游戏模板中查看\n")
        f.write("5. **背景介绍**直接存储在content字段中\n\n")
        
        f.write("## 注意\n")
        f.write("要获取完整的模板内容，需要：\n")
        f.write("1. 通过各个ID在系统数据库中查询对应的实际内容\n")
        f.write("2. 或者从游戏运行时的完整JSON文件中提取\n")

if __name__ == "__main__":
    full_parse_csv()
    print("解析完成！已生成 顾飞祁案例完整解析.md")