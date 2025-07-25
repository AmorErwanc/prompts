import csv
import json
import pprint

def deep_parse_csv():
    """深度解析CSV中的一条数据，找出所有有用的字段"""
    
    # 读取CSV文件
    with open('/Users/edy/Desktop/project/挑战玩法/好人坏人挑战数据.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    # 选择顾飞祁的案例进行深度解析（第6条）
    target_row = None
    for row in data:
        if '顾飞祁' in row.get('content', ''):
            target_row = row
            break
    
    if not target_row:
        print("未找到顾飞祁案例")
        return
    
    print("=== 深度解析顾飞祁案例 ===\n")
    
    # 解析content字段
    content = json.loads(target_row['content'])
    print("1. Content字段解析：")
    print("-" * 50)
    
    for item in content:
        print(f"\n项目ID: {item.get('id')}")
        print(f"类型: {item.get('type')}")
        
        # 解析content中的内容
        if 'content' in item:
            for idx, c in enumerate(item['content']):
                print(f"\n  内容{idx+1}:")
                print(f"    标题: {c.get('val')}")
                print(f"    类型: {c.get('type')}")
                print(f"    inName: {c.get('inName')}")
                if 'sub' in c:
                    for sub_item in c['sub']:
                        if sub_item.get('val'):
                            print(f"    子内容: {sub_item.get('val')}")
    
    # 解析in_param字段
    print("\n\n2. In_param字段解析：")
    print("-" * 50)
    
    in_param = json.loads(target_row['in_param'])
    
    # 查找所有参数
    print("\n所有参数列表:")
    for i, param in enumerate(in_param):
        print(f"\n参数{i+1}:")
        print(f"  inName: {param.get('inName')}")
        print(f"  outName: {param.get('outName')}")
        print(f"  chainId: {param.get('chainId')}")
        print(f"  type: {param.get('type')}")
        if 'val' in param:
            val = param['val']
            if isinstance(val, str):
                if len(val) > 100:
                    print(f"  val: {val[:100]}...")
                else:
                    print(f"  val: {val}")
            else:
                print(f"  val: {val}")
                
    # 提取关键内容
    print("\n\n关键内容提取:")
    for param in in_param:
        # 系统提示词
        if 'val' in param and isinstance(param.get('val'), str):
            if '你是{{system_1}}' in param['val']:
                print("\n[系统提示词完整内容]")
                print(param['val'])
                
            # 模型信息
            if param.get('inName') == 'model':
                print(f"\n[使用模型]: {param['val']}")
                
            # 角色相关ID
            if param.get('inName') == 'system_1':
                print(f"\n[角色ID]: {param['val']}")
            elif param.get('inName') == 'system_4':
                print(f"\n[内在人设ID]: {param['val']}")
            elif param.get('inName') == 'initChat_2':
                print(f"\n[开场白ID]: {param['val']}")
    
    # 提取所有ID映射
    print("\n\n3. ID映射关系：")
    print("-" * 50)
    
    id_mappings = {}
    for param in in_param:
        if 'inName' in param and 'outName' in param and param.get('val'):
            if param['inName'].startswith('system_'):
                id_mappings[param['inName']] = {
                    'id': param['val'],
                    'outName': param['outName']
                }
    
    for key, value in id_mappings.items():
        print(f"{key}: {value}")
    
    # 查找具体的值
    print("\n\n4. 查找具体内容：")
    print("-" * 50)
    
    # 从content中找背景介绍
    for item in content:
        if 'content' in item:
            for c in item['content']:
                if 'sub' in c:
                    for sub in c['sub']:
                        if sub.get('val') and '顾飞祁' in sub.get('val', ''):
                            print(f"\n背景介绍内容:")
                            print(sub['val'])
                            if 'outName' in sub:
                                print(f"对应ID: {sub['outName']}")

if __name__ == "__main__":
    deep_parse_csv()