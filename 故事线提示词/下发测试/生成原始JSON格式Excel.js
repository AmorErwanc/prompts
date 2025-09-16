const fs = require('fs');
const path = require('path');

// 生成保持JSON原始格式的Excel测试集
function generateOriginalFormatExcel() {
    console.log('🚀 开始生成原始JSON格式Excel测试集...\n');
    
    try {
        // 生成测试数据（保持原始JSON格式）
        const testData = generateOriginalTestSet();
        
        console.log(`\n📊 数据统计:`);
        console.log(`总测试用例: ${testData.length}个`);
        console.log(`可以中断: ${testData.filter(item => item.idealAnswer === 'TRUE').length}个`);
        console.log(`不能中断: ${testData.filter(item => item.idealAnswer === 'FALSE').length}个`);
        
        // 生成CSV格式（保持JSON原始格式）
        const csvContent = generateOriginalCSV(testData);
        const csvPath = '/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/原始格式测试数据集.csv';
        fs.writeFileSync(csvPath, csvContent, 'utf8');
        
        console.log(`\n✅ 原始格式CSV测试集生成完成！`);
        console.log(`📁 文件路径: ${csvPath}`);
        
        // 生成Excel XML（保持JSON原始格式）
        const excelXML = generateOriginalExcelXML(testData);
        const excelPath = '/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/原始格式测试数据集.xlsx';
        fs.writeFileSync(excelPath, excelXML, 'utf8');
        
        console.log(`📊 生成原始格式Excel文件: ${excelPath}`);
        
        // 生成场景分布统计
        generateStatistics(testData);
        
        console.log(`\n💡 提示：Excel文件中完整保留了JSON的原始对话格式`);
        
    } catch (error) {
        console.error('❌ 生成失败:', error.message);
    }
}

// 生成原始格式测试数据集
function generateOriginalTestSet() {
    const testData = [];
    
    // 1. 处理可以中断的测试数据（6个）
    console.log('📥 处理可以中断的测试数据...');
    const canInterruptPath = '/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/可以中断的测试数据';
    
    for (let i = 1; i <= 6; i++) {
        const testDir = path.join(canInterruptPath, `测试数据${i}`);
        const historicalPath = path.join(testDir, 'historical_context.json');
        const currentPath = path.join(testDir, 'current_dialogue.json');
        
        if (fs.existsSync(historicalPath) && fs.existsSync(currentPath)) {
            const historical = JSON.parse(fs.readFileSync(historicalPath, 'utf8'));
            const current = JSON.parse(fs.readFileSync(currentPath, 'utf8'));
            
            testData.push({
                testId: `可中断-${i}`,
                historical: JSON.stringify(historical, null, 2),  // 保持JSON格式
                current: JSON.stringify(current, null, 2),        // 保持JSON格式
                idealAnswer: 'TRUE',
                scenario: getScenarioType(current[0]?.content || '', true)
            });
            console.log(`✅ 处理完成: 可中断测试数据${i}`);
        }
    }
    
    // 2. 处理不能中断的测试数据（选择前20个代表性数据）
    console.log('📥 处理不能中断的测试数据（选择代表性数据）...');
    const cannotInterruptPath = '/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/不能中断的测试数据';
    
    // 选择有代表性的不能中断数据
    const selectedIndices = [1, 2, 3, 4, 5, 6, 8, 9, 11, 12, 13, 15, 17, 19, 20, 23, 24, 25, 28, 31];
    
    selectedIndices.forEach(i => {
        const testDir = path.join(cannotInterruptPath, `测试数据${i}`);
        const historicalPath = path.join(testDir, 'historical_context.json');
        const currentPath = path.join(testDir, 'current_dialogue.json');
        
        if (fs.existsSync(historicalPath) && fs.existsSync(currentPath)) {
            const historical = JSON.parse(fs.readFileSync(historicalPath, 'utf8'));
            const current = JSON.parse(fs.readFileSync(currentPath, 'utf8'));
            
            testData.push({
                testId: `不可中断-${i}`,
                historical: JSON.stringify(historical, null, 2),  // 保持JSON格式
                current: JSON.stringify(current, null, 2),        // 保持JSON格式
                idealAnswer: 'FALSE',
                scenario: getScenarioType(current[0]?.content || '', false)
            });
            console.log(`✅ 处理完成: 不可中断测试数据${i}`);
        }
    });
    
    return testData;
}

// 场景类型判断
function getScenarioType(userContent, canInterrupt) {
    if (canInterrupt) {
        if (userContent.includes('……') || userContent === '……') return '情感暂停-可中断';
        if (userContent.includes('（') && userContent.includes('）')) return '行为完成-可中断';
        return '对话结束-可中断';
    } else {
        if (userContent.includes('？')) return '质疑提问-不可中断';
        if (userContent.includes('……')) return '情感思考-不可中断';
        if (['有病', '废话真多', '不甘心'].some(word => userContent.includes(word))) return '情绪激化-不可中断';
        if (userContent.includes('（') && userContent.includes('）')) return '关键行为-不可中断';
        return '连贯对话-不可中断';
    }
}

// 生成原始格式CSV
function generateOriginalCSV(testData) {
    const BOM = '\uFEFF';  // 添加BOM确保Excel正确识别UTF-8
    const headers = ['测试编号', '历史对话', '当前对话', '参照回答', '场景类型'];
    
    const csvRows = [headers.join(',')];
    
    testData.forEach(item => {
        const escapeCSV = (text) => {
            if (typeof text !== 'string') return text;
            // 对于JSON字符串，需要转义引号并用引号包围
            const needsQuotes = text.includes(',') || text.includes('"') || text.includes('\n') || text.includes('\r');
            if (needsQuotes) {
                return `"${text.replace(/"/g, '""')}"`;
            }
            return text;
        };
        
        const row = [
            escapeCSV(item.testId),
            escapeCSV(item.historical),
            escapeCSV(item.current),
            item.idealAnswer,
            escapeCSV(item.scenario)
        ];
        
        csvRows.push(row.join(','));
    });
    
    return BOM + csvRows.join('\n');
}

// 生成原始格式Excel XML
function generateOriginalExcelXML(testData) {
    const header = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:x="urn:schemas-microsoft-com:office:excel"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:html="http://www.w3.org/TR/REC-html40">
 <DocumentProperties xmlns="urn:schemas-microsoft-com:office:office">
  <Title>故事线商业化测试数据集（原始JSON格式）</Title>
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
 <Worksheet ss:Name="测试数据集">
  <Table ss:ExpandedColumnCount="5" ss:ExpandedRowCount="${testData.length + 1}">
   <Column ss:AutoFitWidth="0" ss:Width="80"/>
   <Column ss:AutoFitWidth="0" ss:Width="400"/>
   <Column ss:AutoFitWidth="0" ss:Width="300"/>
   <Column ss:AutoFitWidth="0" ss:Width="80"/>
   <Column ss:AutoFitWidth="0" ss:Width="120"/>`;
    
    const footer = `  </Table>
 </Worksheet>
</Workbook>`;
    
    // 生成表头
    let rows = `
   <Row ss:Height="20">
    <Cell ss:StyleID="Header"><Data ss:Type="String">测试编号</Data></Cell>
    <Cell ss:StyleID="Header"><Data ss:Type="String">历史对话</Data></Cell>
    <Cell ss:StyleID="Header"><Data ss:Type="String">当前对话</Data></Cell>
    <Cell ss:StyleID="Header"><Data ss:Type="String">参照回答</Data></Cell>
    <Cell ss:StyleID="Header"><Data ss:Type="String">场景类型</Data></Cell>
   </Row>`;
    
    // 生成数据行
    testData.forEach(item => {
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
   </Row>`;
    });
    
    return header + rows + footer;
}

// 生成统计信息
function generateStatistics(testData) {
    const scenarios = {};
    testData.forEach(item => {
        scenarios[item.scenario] = (scenarios[item.scenario] || 0) + 1;
    });
    
    console.log(`\n📈 场景分布统计:`);
    Object.entries(scenarios).forEach(([scenario, count]) => {
        console.log(`${scenario}: ${count}个`);
    });
}

// 运行主程序
generateOriginalFormatExcel();