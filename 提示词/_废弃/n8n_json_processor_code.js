// N8N Code节点 - JSON去转义和引号替换处理器
// 作者：Claude Code
// 功能：1. JSON字符串去转义 2. 将正文中的英文引号替换为中文引号

// 获取输入数据
const inputData = $input.all();

// 智能数据提取函数 - 从复杂的嵌套对象中找到需要处理的JSON字符串
function extractJsonContent(data) {
    // 如果直接是字符串，检查是否为JSON格式
    if (typeof data === 'string') {
        const trimmed = data.trim();
        if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
            return data;
        }
        return null;
    }
    
    // 如果是数组，递归检查每个元素
    if (Array.isArray(data)) {
        for (let i = 0; i < data.length; i++) {
            const result = extractJsonContent(data[i]);
            if (result) return result;
        }
    }
    
    // 如果是对象，递归查找可能的JSON字符串
    if (data && typeof data === 'object') {
        // 优先查找常见的字段名
        const possibleFields = ['content', 'message', 'data', 'json', 'text', 'body'];
        
        for (const field of possibleFields) {
            if (data[field]) {
                if (typeof data[field] === 'string') {
                    // 检查是否像JSON字符串
                    const trimmed = data[field].trim();
                    if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
                        return data[field];
                    }
                } else if (typeof data[field] === 'object') {
                    // 递归搜索
                    const result = extractJsonContent(data[field]);
                    if (result) return result;
                }
            }
        }
        
        // 如果没找到，递归搜索所有字段
        for (const key in data) {
            if (data.hasOwnProperty(key)) {
                const result = extractJsonContent(data[key]);
                if (result) return result;
            }
        }
    }
    
    return null;
}

// JSON清理函数 - 处理可能导致解析失败的特殊情况
function cleanJsonString(jsonString) {
    return jsonString
        // 移除可能存在的BOM字符
        .replace(/^\uFEFF/, '')
        // 移除字符串开头和结尾的多余空白字符
        .trim()
        // 处理可能的控制字符问题
        .replace(/[\x00-\x1F\x7F]/g, function(match) {
            // 保留有效的转义字符，移除其他控制字符
            switch(match) {
                case '\n': return '\\n';
                case '\t': return '\\t';
                case '\r': return '\\r';
                case '\b': return '\\b';
                case '\f': return '\\f';
                default: return '';
            }
        });
}

// 处理函数
function processJsonData(jsonString) {
    try {
        // 首先清理JSON字符串
        jsonString = cleanJsonString(jsonString);
        // 功能1：JSON去转义
        // 处理复杂的转义字符情况，特别是嵌套引号的处理
        let unescapedJson = jsonString;
        
        console.log('原始JSON长度:', unescapedJson.length);
        console.log('第1130-1140字符:', unescapedJson.substring(1130, 1140));
        
        // 修复特定的问题模式：处理结尾的多余转义引号
        // 模式如：\"文本内容\"\"" 应该修复为 \"文本内容\""
        unescapedJson = unescapedJson.replace(/\\"([^"]*)\\"\\"/g, '\\"$1\\"');
        
        console.log('修复多余引号后的第1130-1140字符:', unescapedJson.substring(1130, 1140));
        
        // 现在按正确顺序处理转义字符
        unescapedJson = unescapedJson
            .replace(/\\\\/g, '\\')          // 首先处理双反斜杠 -> 单反斜杠
            .replace(/\\"/g, '"')            // 还原双引号
            .replace(/\\'/g, "'")            // 还原单引号
            .replace(/\\n/g, '\n')           // 还原换行符
            .replace(/\\t/g, '\t')           // 还原制表符
            .replace(/\\r/g, '\r')           // 还原回车符
            .replace(/\\b/g, '\b')           // 还原退格符
            .replace(/\\f/g, '\f')           // 还原换页符
            .replace(/\\u([0-9a-fA-F]{4})/g, (_, p1) => String.fromCharCode(parseInt(p1, 16))); // 处理Unicode转义
        
        console.log('去转义完成');
        console.log('去转义后的前200个字符:', unescapedJson.substring(0, 200));
        
        // 解析JSON以验证格式正确性
        let parsedJson;
        try {
            parsedJson = JSON.parse(unescapedJson);
        } catch (parseError) {
            console.error('JSON解析详细错误:', parseError.message);
            console.error('错误位置附近的内容:', unescapedJson.substring(Math.max(0, parseError.position - 50), parseError.position + 50));
            throw parseError;
        }
        
        // 功能2：将正文内容中的英文引号替换为中文引号
        // 这样可以避免JSON内部的引号与JSON结构的引号冲突
        function replaceQuotesInContent(obj) {
            if (typeof obj === 'string') {
                // 将英文双引号替换为中文双引号，避免JSON解析冲突
                return obj
                    .replace(/"/g, '\u201c')      // 英文双引号替换为中文左双引号
                    .replace(/'/g, '\u2018');     // 英文单引号替换为中文左单引号
            } else if (Array.isArray(obj)) {
                return obj.map(item => replaceQuotesInContent(item));
            } else if (obj !== null && typeof obj === 'object') {
                const newObj = {};
                for (let key in obj) {
                    newObj[key] = replaceQuotesInContent(obj[key]);
                }
                return newObj;
            }
            return obj;
        }
        
        // 应用引号替换
        let processedJson = replaceQuotesInContent(parsedJson);
        
        console.log('引号替换完成');
        
        return {
            success: true,
            original: jsonString,
            processed: processedJson,
            processedString: JSON.stringify(processedJson, null, 2),
            message: 'JSON处理成功：去转义完成，英文引号已替换为中文引号'
        };
        
    } catch (error) {
        console.error('JSON处理失败:', error.message);
        return {
            success: false,
            error: error.message,
            original: jsonString,
            message: 'JSON处理失败，请检查输入格式'
        };
    }
}

// 处理所有输入项目
const processedItems = [];

for (let i = 0; i < inputData.length; i++) {
    const item = inputData[i];
    
    console.log('处理输入项目:', i);
    
    // 智能提取JSON数据
    let jsonData = extractJsonContent(item);
    
    if (!jsonData) {
        // 如果智能提取失败，使用原来的逻辑作为后备
        if (typeof item.json === 'string') {
            jsonData = item.json;
        } else if (item.json && typeof item.json === 'object') {
            jsonData = JSON.stringify(item.json);
        } else if (typeof item === 'string') {
            jsonData = item;
        } else {
            jsonData = JSON.stringify(item);
        }
    }
    
    console.log('提取的JSON数据长度:', jsonData.length);
    console.log('JSON数据开头:', jsonData.substring(0, 100) + '...');
    
    // 处理JSON数据
    const result = processJsonData(jsonData);
    
    processedItems.push({
        json: result
    });
}

// 返回处理结果
return processedItems;

/*
使用说明：
1. 将此代码复制到N8N工作流中的Code节点
2. 代码支持智能数据提取，会自动从复杂的嵌套结构中找到需要处理的JSON字符串
3. 支持的输入格式：
   - 直接的JSON字符串
   - 包含content/message/data/json等字段的对象
   - 复杂的API响应结构（如OpenAI API响应）
   - 任何嵌套的对象结构
4. 处理功能：
   - 完整的JSON转义字符处理（\n, \", \\, \t, \r, \b, \f, Unicode）
   - 英文引号替换为中文引号，避免JSON解析冲突
   - 智能错误处理和详细日志输出
5. 输出结果包含：
   - success: 处理是否成功
   - original: 原始输入数据
   - processed: 处理后的JSON对象
   - processedString: 处理后的JSON字符串（格式化）
   - message: 处理结果消息
   - error: 错误信息（如果失败）

示例输入（复杂API响应）：
{
  "choices": [{
    "message": {
      "content": "{\"chapter_title\": \"月下情定\",\"chapter_story\": \"夜色如墨...\"}"
    }
  }]
}

示例输出：
{
  "success": true,
  "processed": {
    "chapter_title": "月下情定",
    "chapter_story": "夜色如墨...",
    ...
  },
  "message": "JSON处理成功：去转义完成，英文引号已替换为中文引号"
}
*/