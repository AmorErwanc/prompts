// n8n Code节点的完整错误处理代码
// 处理模型各种可能的异常输出
// 版本: 2.0
// 更新日期: 2025-07-24
// 
// 更新历史:
// v2.0 - 增加了更多错误恢复策略:
//   - 处理中文引号和特殊字符
//   - 处理BOM字符和Unicode转义
//   - 处理数组格式输入
//   - 添加4种JSON修复策略
//   - 增强调试信息输出
// v1.0 - 基础版本，处理常见错误情况

const items = $input.all();
const outputArray = [];

for (const item of items) {
  let result = {
    success: false,
    error_type: null,
    error_message: null,
    original_output: null,
    timestamp: new Date().toISOString()
  };
  
  try {
    // 获取模型输出 - 处理不同的输入格式
    const modelOutput = item.output || item.model_output || item.response || 
                       item.json?.output || item.json?.model_output || item.json?.response;
    result.original_output = modelOutput;
    
    // 情况1: 输出为空或undefined
    if (!modelOutput) {
      throw {
        type: 'empty_output',
        message: '模型输出为空'
      };
    }
    
    // 情况2: 输出不是字符串（可能已经是对象）
    let parsedData;
    if (typeof modelOutput === 'object') {
      // 如果是数组，尝试提取第一个元素
      if (Array.isArray(modelOutput)) {
        if (modelOutput.length > 0) {
          // 如果数组第一个元素有output属性，使用它
          if (modelOutput[0].output) {
            const innerOutput = modelOutput[0].output;
            // 递归处理这个output
            if (typeof innerOutput === 'string') {
              // 将字符串标记为需要解析
              parsedData = null;
              modelOutput = innerOutput;
            } else {
              parsedData = innerOutput;
            }
          } else {
            parsedData = modelOutput[0];
          }
        } else {
          throw {
            type: 'empty_array',
            message: '模型返回了空数组'
          };
        }
      } else {
        parsedData = modelOutput;
      }
    }
    
    // 如果parsedData还是null，说明需要解析字符串
    if (!parsedData && typeof modelOutput === 'string') {
      // 情况3: 清理可能的格式问题
      let cleanedOutput = modelOutput.trim();
      
      // 移除可能的markdown代码块标记
      cleanedOutput = cleanedOutput.replace(/^```json\s*\n?/, '');
      cleanedOutput = cleanedOutput.replace(/\n?```\s*$/, '');
      
      // 移除可能的前后空白字符
      cleanedOutput = cleanedOutput.trim();
      
      // 情况4: 模型可能返回了额外的文字说明
      // 尝试提取JSON部分（查找第一个{到最后一个}）
      const jsonMatch = cleanedOutput.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        cleanedOutput = jsonMatch[0];
      }
      
      // 情况5: 处理转义字符问题
      // 有时模型会过度转义
      cleanedOutput = cleanedOutput.replace(/\\"/g, '"');
      cleanedOutput = cleanedOutput.replace(/\\\\/g, '\\');
      
      // 情况5.1: 处理模型可能输出的中文引号
      cleanedOutput = cleanedOutput.replace(/[""]/g, '"');
      cleanedOutput = cleanedOutput.replace(/['']/g, "'");
      
      // 情况5.2: 处理可能的换行符转义问题
      cleanedOutput = cleanedOutput.replace(/\\n/g, '\n');
      cleanedOutput = cleanedOutput.replace(/\\r/g, '\r');
      cleanedOutput = cleanedOutput.replace(/\\t/g, '\t');
      
      // 情况5.3: 处理模型可能添加的BOM字符
      if (cleanedOutput.charCodeAt(0) === 0xFEFF) {
        cleanedOutput = cleanedOutput.substring(1);
      }
      
      // 情况5.4: 处理模型可能输出的Unicode转义序列
      cleanedOutput = cleanedOutput.replace(/\\u[\dA-F]{4}/gi, (match) => {
        return String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16));
      });
      
      // 情况5.5: 处理可能的额外反斜杠（模型有时会多加反斜杠）
      if (cleanedOutput.includes('\\\\\\')) {
        cleanedOutput = cleanedOutput.replace(/\\\\\\\\/g, '\\\\');
        cleanedOutput = cleanedOutput.replace(/\\\\\"/g, '"');
      }
      
      // 情况5.6: 处理模型可能在JSON中使用单引号的情况
      // 但要小心不要破坏值中的单引号
      if (!cleanedOutput.includes('"') && cleanedOutput.includes("'")) {
        // 只有在完全没有双引号但有单引号时才替换
        cleanedOutput = cleanedOutput.replace(/'/g, '"');
      }
      
      try {
        parsedData = JSON.parse(cleanedOutput);
      } catch (parseError) {
        // 情况6: JSON格式错误，尝试一些恢复策略
        
        // 恢复策略1: 尝试修复缺失的逗号
        let fixedOutput = cleanedOutput.replace(/}\s*"/g, '}, "');
        fixedOutput = fixedOutput.replace(/"\s*"/g, '", "');
        fixedOutput = fixedOutput.replace(/]\s*"/g, '], "');
        
        try {
          parsedData = JSON.parse(fixedOutput);
        } catch (e1) {
          // 恢复策略2: 尝试修复末尾的逗号
          fixedOutput = cleanedOutput.replace(/,\s*}/g, '}');
          fixedOutput = fixedOutput.replace(/,\s*]/g, ']');
          
          try {
            parsedData = JSON.parse(fixedOutput);
          } catch (e2) {
            // 恢复策略3: 尝试添加缺失的引号
            // 查找类似 key: value 的模式并添加引号
            fixedOutput = cleanedOutput.replace(/([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:/g, '$1"$2":');
            
            try {
              parsedData = JSON.parse(fixedOutput);
            } catch (e3) {
              // 恢复策略4: 如果模型输出了类似Python字典的格式
              // 将None转为null，True/False转为true/false
              fixedOutput = cleanedOutput
                .replace(/\bNone\b/g, 'null')
                .replace(/\bTrue\b/g, 'true')
                .replace(/\bFalse\b/g, 'false');
              
              try {
                parsedData = JSON.parse(fixedOutput);
              } catch (e4) {
                // 所有恢复策略都失败了
                throw {
                  type: 'json_parse_error',
                  message: `JSON解析失败: ${parseError.message}`,
                  cleaned_output: cleanedOutput,
                  recovery_attempts: [
                    { strategy: 'fix_missing_commas', error: e1.message },
                    { strategy: 'fix_trailing_commas', error: e2.message },
                    { strategy: 'fix_unquoted_keys', error: e3.message },
                    { strategy: 'fix_python_format', error: e4.message }
                  ]
                };
              }
            }
          }
        }
      }
    } else {
      // 情况7: 输出类型异常
      throw {
        type: 'invalid_type',
        message: `期望字符串或对象，但收到: ${typeof modelOutput}`
      };
    }
    
    // 情况8: 解析成功但格式不符合预期
    if (!parsedData.assistant_reply) {
      throw {
        type: 'missing_required_field',
        message: '缺少必需字段: assistant_reply'
      };
    }
    
    if (!parsedData.intent_type) {
      throw {
        type: 'missing_required_field',
        message: '缺少必需字段: intent_type'
      };
    }
    
    // 情况9: intent_type值不在预期范围内
    const validIntentTypes = ['clarify', 'preview', 'new_plan', 'modify_step', 'chat_only'];
    if (!validIntentTypes.includes(parsedData.intent_type)) {
      throw {
        type: 'invalid_intent_type',
        message: `无效的intent_type: ${parsedData.intent_type}，应该是: ${validIntentTypes.join(', ')}`
      };
    }
    
    // 情况10: template_type值验证（如果不为null）
    const validTemplateTypes = ['judgment', 'affinity', 'emotion', 'switch', 'campus'];
    if (parsedData.template_type && parsedData.template_type !== 'null' && !validTemplateTypes.includes(parsedData.template_type)) {
      throw {
        type: 'invalid_template_type',
        message: `无效的template_type: ${parsedData.template_type}，应该是: ${validTemplateTypes.join(', ')} 或 null`
      };
    }
    
    // 构建输出数据
    const baseOutput = {
      assistant_reply: parsedData.assistant_reply,
      intent_type: parsedData.intent_type,
      target_step: parsedData.target_step === 'null' ? null : parsedData.target_step,
      template_type: parsedData.template_type === 'null' ? null : parsedData.template_type
    };
    
    // 情况11: new_plan类型的额外验证
    if (parsedData.intent_type === 'new_plan') {
      if (!parsedData.character_info) {
        throw {
          type: 'missing_new_plan_field',
          message: 'new_plan类型缺少必需字段: character_info'
        };
      }
      
      if (!parsedData.planning_brief) {
        throw {
          type: 'missing_new_plan_field',
          message: 'new_plan类型缺少必需字段: planning_brief'
        };
      }
      
      // 验证character_info的子字段
      const requiredCharFields = ['name', 'gender', 'features'];
      for (const field of requiredCharFields) {
        if (!parsedData.character_info[field]) {
          throw {
            type: 'missing_character_info_field',
            message: `character_info缺少必需字段: ${field}`
          };
        }
      }
      
      baseOutput.character_info = parsedData.character_info;
      baseOutput.planning_brief = parsedData.planning_brief;
    }
    
    // 情况12: 处理可能的额外字段（记录但不报错）
    const expectedFields = ['assistant_reply', 'intent_type', 'target_step', 'template_type', 'character_info', 'planning_brief'];
    const extraFields = Object.keys(parsedData).filter(key => !expectedFields.includes(key));
    if (extraFields.length > 0) {
      baseOutput._extra_fields = extraFields;
      baseOutput._warning = `发现额外字段: ${extraFields.join(', ')}`;
    }
    
    // 成功解析，将所有字段平铺到结果对象
    result = {
      success: true,
      error_type: null,
      error_message: null,
      timestamp: result.timestamp,
      original_output: result.original_output,
      
      // 基础字段
      assistant_reply: baseOutput.assistant_reply,
      intent_type: baseOutput.intent_type,
      target_step: baseOutput.target_step,
      template_type: baseOutput.template_type
    };
    
    // 如果是new_plan，添加额外字段
    if (baseOutput.character_info) {
      result.character_info = baseOutput.character_info;
    }
    if (baseOutput.planning_brief) {
      result.planning_brief = baseOutput.planning_brief;
    }
    
    // 如果有警告信息，也添加
    if (baseOutput._warning) {
      result._warning = baseOutput._warning;
    }
    if (baseOutput._extra_fields) {
      result._extra_fields = baseOutput._extra_fields;
    }
    
  } catch (error) {
    result.success = false;
    
    if (error.type) {
      // 自定义错误
      result.error_type = error.type;
      result.error_message = error.message;
      if (error.cleaned_output) {
        result.cleaned_output = error.cleaned_output;
      }
      if (error.recovery_attempts) {
        result.recovery_attempts = error.recovery_attempts;
      }
    } else {
      // 系统错误
      result.error_type = 'system_error';
      result.error_message = error.message || '未知错误';
      result.stack_trace = error.stack;
    }
    
    // 添加调试信息
    result.debug_info = {
      input_type: typeof item,
      input_keys: Object.keys(item || {}),
      model_output_type: typeof result.original_output,
      model_output_length: result.original_output ? result.original_output.length : 0
    };
  }
  
  outputArray.push({
    json: result
  });
}

return outputArray;