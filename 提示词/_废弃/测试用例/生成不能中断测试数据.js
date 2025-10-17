const fs = require('fs');
const path = require('path');

// 读取原始对话数据，去除JavaScript注释和标记
let rawContent = fs.readFileSync('/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/中断示例.js', 'utf8');

// 去除注释行和分隔线
rawContent = rawContent
    .split('\n')
    .filter(line => !line.includes('//'))
    .filter(line => !line.includes('----------------'))
    .join('\n');

const rawData = JSON.parse(rawContent);

// 已知的可以中断的轮次位置（基于current_dialogue.json的内容）
const canInterruptRounds = [
    { roundIndex: 32, userContent: "……" },      // 测试数据1
    { roundIndex: 49, userContent: "指什么？" },   // 测试数据2  
    { roundIndex: 88, userContent: "（推开他）" }, // 测试数据3
    { roundIndex: 95, userContent: "（打120）" }, // 测试数据4
    { roundIndex: 113, userContent: "（回家）" },  // 测试数据5
    { roundIndex: 137, userContent: "（休息）" }   // 测试数据6
];

// 将对话数据按轮次分组 (user + assistant = 1轮)
function groupIntoRounds(dialogues) {
    const rounds = [];
    for (let i = 0; i < dialogues.length; i += 2) {
        if (i + 1 < dialogues.length) {
            rounds.push({
                roundNumber: Math.floor(i / 2) + 1,
                user: dialogues[i],
                assistant: dialogues[i + 1],
                startIndex: i
            });
        }
    }
    return rounds;
}

// 获取所有轮次
const allRounds = groupIntoRounds(rawData);
console.log(`总共找到 ${allRounds.length} 轮对话`);

// 筛选不能中断的轮次（排除可以中断的轮次）
const canInterruptIndices = canInterruptRounds.map(r => r.roundIndex);
const cannotInterruptRounds = allRounds.filter((round, index) => {
    // 从第3轮开始，排除可以中断的轮次
    const dataIndex = index * 2; // 对应原始数据中的索引
    return round.roundNumber >= 3 && !canInterruptIndices.includes(dataIndex);
});

console.log(`筛选出 ${cannotInterruptRounds.length} 个不能中断的轮次`);

// 创建基础目录
const baseDir = '/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/不能中断的测试数据';
if (!fs.existsSync(baseDir)) {
    fs.mkdirSync(baseDir, { recursive: true });
}

// 为每个不能中断的轮次生成测试数据
cannotInterruptRounds.forEach((round, index) => {
    const testDataNum = index + 7; // 从7开始编号（前6个已存在）
    const testDir = path.join(baseDir, `测试数据${testDataNum}`);
    
    // 创建测试数据目录
    if (!fs.existsSync(testDir)) {
        fs.mkdirSync(testDir, { recursive: true });
    }
    
    // 生成历史上下文（到当前轮次之前的所有对话）
    const historicalContext = rawData.slice(0, round.startIndex);
    
    // 生成当前对话（当前轮次的user+assistant）
    const currentDialogue = [round.user, round.assistant];
    
    // 写入文件
    fs.writeFileSync(
        path.join(testDir, 'historical_context.json'),
        JSON.stringify(historicalContext, null, 4)
    );
    
    fs.writeFileSync(
        path.join(testDir, 'current_dialogue.json'), 
        JSON.stringify(currentDialogue, null, 4)
    );
    
    console.log(`已生成测试数据${testDataNum}: 第${round.roundNumber}轮 - "${round.user.content}"`);
});

console.log(`\n✅ 自动生成完成！共生成 ${cannotInterruptRounds.length} 个不能中断的测试数据`);
console.log(`📁 保存路径: ${baseDir}`);

// 生成统计报告
const report = {
    totalRounds: allRounds.length,
    canInterruptRounds: canInterruptRounds.length,
    cannotInterruptRounds: cannotInterruptRounds.length,
    generatedTestData: cannotInterruptRounds.length,
    canInterruptDetails: canInterruptRounds,
    cannotInterruptSummary: cannotInterruptRounds.map(round => ({
        testDataNumber: cannotInterruptRounds.indexOf(round) + 7,
        roundNumber: round.roundNumber,
        userContent: round.user.content,
        reason: analyzeWhyCannotInterrupt(round)
    }))
};

// 分析不能中断的原因
function analyzeWhyCannotInterrupt(round) {
    const content = round.user.content;
    const assistantContent = round.assistant.content;
    
    if (content.includes("？") && !content.includes("（")) {
        return "重要质疑提问中";
    } else if (assistantContent.includes("求婚") || assistantContent.includes("戒指")) {
        return "情感表白进行中";
    } else if (assistantContent.includes("匕首") || assistantContent.includes("扭打")) {
        return "危险冲突场景";
    } else if (assistantContent.includes("新人物")) {
        return "新角色出场时";
    } else if (content.includes("……") && !canInterruptRounds.some(r => r.userContent === content)) {
        return "情感思考中";
    } else if (assistantContent.includes("怒") || assistantContent.includes("愤")) {
        return "情绪激化中";
    } else {
        return "对话连贯性要求";
    }
}

// 保存统计报告
fs.writeFileSync(
    '/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/测试数据生成报告.json',
    JSON.stringify(report, null, 4)
);

console.log(`\n📊 已生成统计报告: 测试数据生成报告.json`);