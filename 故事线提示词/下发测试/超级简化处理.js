const fs = require('fs');

// 超级简化处理 - 不依赖JSON.parse
function superSimpleProcess() {
    console.log('🚀 开始超级简化处理...\n');
    
    try {
        const filePath = '/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/中断示例2.js';
        const content = fs.readFileSync(filePath, 'utf8');
        
        // 手动提取对话和中断点
        const { dialogues, interruptPoints } = extractManually(content);
        console.log(`📊 提取完成: ${dialogues.length}条对话, ${interruptPoints.length}个中断点`);
        
        // 组织轮次
        const rounds = createRounds(dialogues);
        console.log(`🔄 组织完成: ${rounds.length}轮对话`);
        
        // 生成样本
        const samples = createSamples(rounds, interruptPoints);
        console.log(`📊 生成样本: ${samples.length}个`);
        
        // 生成文件
        generateFiles(samples);
        
        console.log('\n✅ 超级简化处理完成！');
        
    } catch (error) {
        console.error('❌ 处理失败:', error.message);
    }
}

// 手动提取对话内容
function extractManually(content) {
    const lines = content.split('\n');
    const dialogues = [];
    const interruptPoints = [];
    
    let currentDialogue = null;
    let collectingContent = false;
    let contentLines = [];
    let dialogueIndex = -1;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        // 跳过分隔线
        if (line.startsWith('----')) continue;
        
        // 检测中断标记
        if (line === '//可以结束//') {
            if (dialogueIndex >= 0) {
                interruptPoints.push(dialogueIndex);
                console.log(`🔖 中断点: ${dialogueIndex}`);
            }
            continue;
        }
        
        // 检测对话开始
        if (line === '{') {
            currentDialogue = {};
            collectingContent = false;
            contentLines = [];
            continue;
        }
        
        // 检测角色字段
        if (line.includes('"role":')) {
            const roleMatch = line.match(/"role":\s*"(user|assistant)"/);
            if (roleMatch) {
                currentDialogue.role = roleMatch[1];
            }
            continue;
        }
        
        // 检测内容字段开始
        if (line.includes('"content":')) {
            collectingContent = true;
            // 提取引号内容
            const contentMatch = line.match(/"content":\s*"(.*)"/);
            if (contentMatch) {
                // 单行内容
                currentDialogue.content = contentMatch[1];
                collectingContent = false;
            } else {
                // 多行内容开始
                const startMatch = line.match(/"content":\s*"(.*)$/);
                if (startMatch) {
                    contentLines = [startMatch[1]];
                }
            }
            continue;
        }
        
        // 收集多行内容
        if (collectingContent && line !== '}' && !line.endsWith('},')) {
            contentLines.push(line);
            continue;
        }
        
        // 检测对话结束
        if ((line === '}' || line.endsWith('},')) && currentDialogue && currentDialogue.role) {
            // 处理多行内容
            if (contentLines.length > 0) {
                // 合并内容并移除最后的引号
                let fullContent = contentLines.join('\n');
                if (fullContent.endsWith('"')) {
                    fullContent = fullContent.slice(0, -1);
                }
                currentDialogue.content = fullContent;
            }
            
            // 添加对话到列表
            dialogues.push(currentDialogue);
            dialogueIndex++;
            console.log(`💬 对话${dialogueIndex}: ${currentDialogue.role} - "${currentDialogue.content.substring(0, 30)}..."`);
            
            // 重置状态
            currentDialogue = null;
            collectingContent = false;
            contentLines = [];
        }
    }
    
    return { dialogues, interruptPoints };
}

// 创建轮次（user + assistant = 1轮）
function createRounds(dialogues) {
    const rounds = [];
    let roundNumber = 1;
    
    // 跳过第一个系统消息（如果存在）
    let startIndex = 0;
    if (dialogues[0] && dialogues[0].content === "下面我们开始正式情节。") {
        startIndex = 1;
    }
    
    for (let i = startIndex; i < dialogues.length - 1; i += 2) {
        const userMsg = dialogues[i];
        const assistantMsg = dialogues[i + 1];
        
        if (userMsg && userMsg.role === 'user' && 
            assistantMsg && assistantMsg.role === 'assistant') {
            
            rounds.push({
                roundNumber: roundNumber++,
                user: userMsg,
                assistant: assistantMsg,
                dialogueIndex: i
            });
            
            console.log(`🔄 轮次${roundNumber-1}: "${userMsg.content}" -> 回应长度${assistantMsg.content.length}字符`);
        }
    }
    
    return rounds;
}

// 创建测试样本
function createSamples(rounds, interruptPoints) {
    const samples = [];
    
    // 确定可中断轮次
    const interruptRoundNumbers = new Set();
    
    interruptPoints.forEach(point => {
        // 找到对应的轮次
        for (let round of rounds) {
            // 如果assistant消息在中断点，则该轮次可中断
            if (round.dialogueIndex + 1 === point) {
                interruptRoundNumbers.add(round.roundNumber);
                console.log(`✅ 轮次${round.roundNumber}可中断: "${round.user.content}"`);
                break;
            }
        }
    });
    
    // 生成样本（从第3轮开始）
    rounds.forEach((round, index) => {
        if (round.roundNumber >= 3) {
            // 历史对话
            const historical = [];
            for (let i = 0; i < index; i++) {
                historical.push(rounds[i].user);
                historical.push(rounds[i].assistant);
            }
            
            // 当前对话
            const current = [round.user, round.assistant];
            
            // 判断是否可中断
            const canInterrupt = interruptRoundNumbers.has(round.roundNumber);
            
            samples.push({
                testId: canInterrupt ? `可中断轮次-${round.roundNumber}` : `不可中断轮次-${round.roundNumber}`,
                historical: JSON.stringify(historical, null, 2),
                current: JSON.stringify(current, null, 2),
                idealAnswer: canInterrupt ? 'TRUE' : 'FALSE',
                scenario: determineScenario(round, canInterrupt),
                roundNumber: round.roundNumber
            });
            
            const status = canInterrupt ? '✅' : '❌';
            console.log(`${status} 轮次${round.roundNumber}: "${round.user.content}"`);
        }
    });
    
    return samples;
}

// 确定场景类型
function determineScenario(round, canInterrupt) {
    const userContent = round.user.content;
    const assistantContent = round.assistant.content;
    
    if (canInterrupt) {
        if (userContent === '没事' && assistantContent.includes('分手')) return '冲突结束-可中断';
        if (userContent === '没事') return '情况稳定-可中断';
        if (userContent.includes('……')) return '情感表达-可中断';
        return '对话完成-可中断';
    } else {
        if (userContent.includes('？')) return '疑问待答-不可中断';
        if (userContent === '不给') return '拒绝态度-不可中断';
        if (userContent.includes('不甘心')) return '情绪激化-不可中断';
        if (userContent.includes('有病') || userContent.includes('废话')) return '争执进行-不可中断';
        return '连续对话-不可中断';
    }
}

// 生成文件
function generateFiles(samples) {
    console.log(`\n📊 开始生成文件...`);
    
    // CSV内容
    const BOM = '\uFEFF';
    const headers = ['测试编号', '历史对话', '当前对话', '参照回答', '场景类型', '轮次编号'];
    const csvRows = [headers.join(',')];
    
    samples.forEach(item => {
        const escapeCSV = (text) => {
            if (typeof text !== 'string') return text;
            if (text.includes(',') || text.includes('"') || text.includes('\n')) {
                return `"${text.replace(/"/g, '""')}"`;
            }
            return text;
        };
        
        csvRows.push([
            escapeCSV(item.testId),
            escapeCSV(item.historical),
            escapeCSV(item.current),
            item.idealAnswer,
            escapeCSV(item.scenario),
            item.roundNumber
        ].join(','));
    });
    
    // 写入CSV
    const csvContent = BOM + csvRows.join('\n');
    const csvPath = '/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/超级简化测试集.csv';
    fs.writeFileSync(csvPath, csvContent, 'utf8');
    
    // 生成Excel XML
    const excelXML = generateExcelXML(samples);
    const excelPath = '/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/超级简化测试集.xlsx';
    fs.writeFileSync(excelPath, excelXML, 'utf8');
    
    console.log(`✅ CSV文件: ${csvPath}`);
    console.log(`📊 Excel文件: ${excelPath}`);
    
    // 统计
    const trueCount = samples.filter(s => s.idealAnswer === 'TRUE').length;
    const falseCount = samples.filter(s => s.idealAnswer === 'FALSE').length;
    
    console.log(`\n📈 最终统计:`);
    console.log(`总样本: ${samples.length}个`);
    console.log(`可中断: ${trueCount}个`);
    console.log(`不可中断: ${falseCount}个`);
    
    // 场景分布
    const scenarios = {};
    samples.forEach(item => {
        scenarios[item.scenario] = (scenarios[item.scenario] || 0) + 1;
    });
    
    console.log(`\n场景分布:`);
    Object.entries(scenarios).forEach(([scenario, count]) => {
        console.log(`${scenario}: ${count}个`);
    });
}

// 生成Excel XML
function generateExcelXML(samples) {
    const header = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:x="urn:schemas-microsoft-com:office:excel"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:html="http://www.w3.org/TR/REC-html40">
 <DocumentProperties xmlns="urn:schemas-microsoft-com:office:office">
  <Title>超级简化测试数据集</Title>
  <Created>${new Date().toISOString()}</Created>
 </DocumentProperties>
 <Styles>
  <Style ss:ID="Header">
   <Font ss:Bold="1"/>
   <Interior ss:Color="#E6E6FA" ss:Pattern="Solid"/>
  </Style>
  <Style ss:ID="TrueAnswer">
   <Interior ss:Color="#90EE90" ss:Pattern="Solid"/>
  </Style>
  <Style ss:ID="FalseAnswer">
   <Interior ss:Color="#FFB6C1" ss:Pattern="Solid"/>
  </Style>
  <Style ss:ID="JsonText">
   <Font ss:FontName="Consolas" ss:Size="9"/>
   <Alignment ss:Vertical="Top" ss:WrapText="1"/>
  </Style>
 </Styles>
 <Worksheet ss:Name="超级简化测试数据">
  <Table ss:ExpandedColumnCount="6" ss:ExpandedRowCount="${samples.length + 1}">
   <Column ss:AutoFitWidth="0" ss:Width="120"/>
   <Column ss:AutoFitWidth="0" ss:Width="400"/>
   <Column ss:AutoFitWidth="0" ss:Width="300"/>
   <Column ss:AutoFitWidth="0" ss:Width="80"/>
   <Column ss:AutoFitWidth="0" ss:Width="120"/>
   <Column ss:AutoFitWidth="0" ss:Width="80"/>
   <Row ss:Height="20">
    <Cell ss:StyleID="Header"><Data ss:Type="String">测试编号</Data></Cell>
    <Cell ss:StyleID="Header"><Data ss:Type="String">历史对话</Data></Cell>
    <Cell ss:StyleID="Header"><Data ss:Type="String">当前对话</Data></Cell>
    <Cell ss:StyleID="Header"><Data ss:Type="String">参照回答</Data></Cell>
    <Cell ss:StyleID="Header"><Data ss:Type="String">场景类型</Data></Cell>
    <Cell ss:StyleID="Header"><Data ss:Type="String">轮次编号</Data></Cell>
   </Row>`;
    
    let rows = '';
    samples.forEach(item => {
        const escapeXML = (text) => {
            if (typeof text !== 'string') return text;
            return text
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&apos;');
        };
        
        const answerStyle = item.idealAnswer === 'TRUE' ? 'TrueAnswer' : 'FalseAnswer';
        
        rows += `
   <Row ss:Height="100">
    <Cell><Data ss:Type="String">${escapeXML(item.testId)}</Data></Cell>
    <Cell ss:StyleID="JsonText"><Data ss:Type="String">${escapeXML(item.historical)}</Data></Cell>
    <Cell ss:StyleID="JsonText"><Data ss:Type="String">${escapeXML(item.current)}</Data></Cell>
    <Cell ss:StyleID="${answerStyle}"><Data ss:Type="String">${item.idealAnswer}</Data></Cell>
    <Cell><Data ss:Type="String">${escapeXML(item.scenario)}</Data></Cell>
    <Cell><Data ss:Type="Number">${item.roundNumber}</Data></Cell>
   </Row>`;
    });
    
    const footer = `
  </Table>
 </Worksheet>
</Workbook>`;
    
    return header + rows + footer;
}

// 运行程序
superSimpleProcess();