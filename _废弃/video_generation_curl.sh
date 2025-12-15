#!/bin/bash

# 百度千帆视频生成API - 标准curl命令
# 使用前请替换以下变量中的占位符

# ===========================================
# 配置变量 - 请修改以下内容
# ===========================================

# 您的Access Token (从获取token的API返回结果中复制)
ACCESS_TOKEN="请替换为您的实际Access_Token"

# 任务ID - 建议使用时间戳+随机数确保唯一性
TASK_ID="task_$(date +%s)_$(shuf -i 1000-9999 -n 1)"

# API端点
API_URL="https://qianfan.baidubce.com/video/generations"

# ===========================================
# curl 命令 - 多行格式 (推荐)
# ===========================================

echo "正在发送视频生成请求..."
echo "任务ID: $TASK_ID"

curl --location "$API_URL" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $ACCESS_TOKEN" \
-d "{
  \"model\": \"musesteamer-2.0-turbo-i2v-audio\",
  \"task_id\": \"$TASK_ID\",
  \"content\": [
    {
      \"type\": \"text\",
      \"text\": \"一位身穿古代盔甲的武士坐在开阔场地的木桌两侧，手持麻将牌进行牌局对战，两人嘴唇微动进行对话。麻将牌整齐排列在桌面的深色棋盘纹布上，背景可见随风飘动的军队旗帜。左边人物说话：\\\"将军，大棚外战火纷飞，咱们在这打麻将不太好吧？\\\" 右边人物说话：\\\"松弛一点！你是不是输钱输怕了？！\\\"\"
    },
    {
      \"type\": \"image_url\",
      \"image_url\": {
        \"url\": \"https://qianfan-document.bj.bcebos.com/images/itv-input-image.png\"
      }
    }
  ],
  \"duration\": 10
}"

echo ""
echo "请求已发送，任务ID: $TASK_ID"
echo "请保存此任务ID以便后续查询结果"