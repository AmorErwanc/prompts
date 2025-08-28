##播客相关提示词
-- prompt data too big .when requirements need data. please stop and request provide.


##播客相关工具##
INSERT INTO agent.tools (id, tool_code, name, description, parameters_json, tool_type, prompt_code, is_async, created_at, updated_at)
VALUES ('2', 'radio_cover', '文本生成图片工具', '根据文本描述生成图片', null, 'hybrid_tool', 'radio_cover', 1, '2025-07-09 14:48:51', '2025-07-16 20:32:13');
INSERT INTO agent.tools (id, tool_code, name, description, parameters_json, tool_type, prompt_code, is_async, created_at, updated_at)
VALUES ('3', 'radio_bgm', '文本生成音乐工具', '根据文本描述生成音乐', null, 'hybrid_tool', 'radio_bgm', 1, '2025-07-09 14:48:51', '2025-07-13 11:36:28');
INSERT INTO agent.tools (id, tool_code, name, description, parameters_json, tool_type, prompt_code, is_async, created_at, updated_at)
VALUES ('5', 'radio_covert_mp3Tool_param', '转换脚本为工具参数字段', '转换脚本为工具参数字段', null, 'prompt_tool', 'radio_covert_mp3Tool_param', 0, '2025-07-09 14:48:51',
        '2025-07-17 21:15:02');
INSERT INTO agent.tools (id, tool_code, name, description, parameters_json, tool_type, prompt_code, is_async, created_at, updated_at)
VALUES ('6', 'radio_outline', '播客大纲', '根据用户输入转换为播客大纲', null, 'prompt_tool', 'radio_outline', 0, '2025-07-09 14:51:18', '2025-07-09 14:51:30');
INSERT INTO agent.tools (id, tool_code, name, description, parameters_json, tool_type, prompt_code, is_async, created_at, updated_at)
VALUES ('7', 'radio_intention', '播客用户输入意图识别', '根据用户输入判断是否想要生成播客', null, 'prompt_tool', 'radio_intention', 0, '2025-07-09 15:02:44',
        '2025-07-09 15:02:44');
INSERT INTO agent.tools (id, tool_code, name, description, parameters_json, tool_type, prompt_code, is_async, created_at, updated_at)
VALUES ('1', 'crawler_tool', '爬虫工具', '根据输入的字符串或URL抓取相关网页内容，支持文本解析和搜索功能', '{
  "type": "object",
  "required": [
    "query"
  ],
  "properties": {
    "query": {
      "type": "string",
      "required": true,
      "description": "输入的字符串或URL，用于解析文章内容"
    },
    "search": {
      "type": "boolean",
      "default": false,
      "required": false,
      "description": "是否执行搜索操作，默认为false"
    },
    "file_url": {
      "type": "string",
      "required": false,
      "description": "可选的文件URL，如果提供，将解析文件内容"
    }
  }
}', 'pure_tool', null, 0, '2025-07-11 10:46:16', '2025-07-11 10:46:16');
INSERT INTO agent.tools (id, tool_code, name, description, parameters_json, tool_type, prompt_code, is_async, created_at, updated_at)
VALUES ('8', 'radio_script', '播客脚本', '前端根据大纲生成展示脚本', null, 'prompt_tool', 'radio_script', 0, '2025-07-12 21:40:56', '2025-07-13 08:51:52');
INSERT INTO agent.tools (id, tool_code, name, description, parameters_json, tool_type, prompt_code, is_async, created_at, updated_at)
VALUES ('9', 'radio_step_name', '播客规划步骤名称', 'radio_step_name', null, 'prompt_tool', 'radio_step_name', 0, '2025-07-19 10:03:33', '2025-07-19 10:03:33');