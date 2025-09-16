# 挑战系统Workflow低代码实现逻辑

## 1. 整体Workflow架构

```mermaid
graph TB
    Start([开始节点]) --> Init[初始化变量节点]
    Init --> LoadConfig[加载配置节点]
    
    LoadConfig --> CheckConfig{配置检测节点}
    CheckConfig -->|配置无效| ErrorHandler[错误处理]
    CheckConfig -->|配置有效| ParseConfig[解析配置]
    
    ParseConfig --> RouteByType{路由分发节点}
    
    %% 不同类型的挑战流程
    RouteByType -->|时间限制型| TimeFlow[时间挑战流程]
    RouteByType -->|轮次限制型| RoundFlow[轮次挑战流程]
    RouteByType -->|判断型| JudgeFlow[判断挑战流程]
    RouteByType -->|数值型| ValueFlow[数值挑战流程]
    
    TimeFlow --> MainLoop[主循环节点]
    RoundFlow --> MainLoop
    JudgeFlow --> MainLoop
    ValueFlow --> MainLoop
    
    MainLoop --> End([结束节点])
    ErrorHandler --> End
    
    style Start fill:#90EE90
    style End fill:#FFB6C1
    style CheckConfig fill:#FFE4B5
    style RouteByType fill:#FFE4B5
```

## 2. 变量定义和初始化流程

```mermaid
graph TD
    subgraph 变量初始化模块
        InitNode[初始化节点] --> SetVars[设置变量节点]
        
        SetVars --> Var1["变量: challengeConfig<br/>类型: Object<br/>默认值: {}"]
        SetVars --> Var2["变量: timeLimit<br/>类型: Number<br/>默认值: null"]
        SetVars --> Var3["变量: roundCount<br/>类型: Number<br/>默认值: null"]
        SetVars --> Var4["变量: targetGoal<br/>类型: String<br/>默认值: null"]
        SetVars --> Var5["变量: currentValue<br/>类型: Number<br/>默认值: 0"]
        SetVars --> Var6["变量: isSuccess<br/>类型: Boolean<br/>默认值: false"]
        SetVars --> Var7["变量: dialogHistory<br/>类型: Array<br/>默认值: []"]
    end
    
    Var1 & Var2 & Var3 & Var4 & Var5 & Var6 & Var7 --> NextNode[下一节点]
```

## 3. Workflow读取配置并验证的核心逻辑

```mermaid
graph TD
    JSONInput["输入JSON配置<br/>{角色名称, 限制条件, 挑战目标...}"] --> ParseJSON[解析JSON节点]
    
    %% 限制条件验证逻辑
    ParseJSON --> CheckLimit{IF节点: 限制条件!=null}
    CheckLimit -->|true| GetLimitType[获取: 限制条件.type]
    CheckLimit -->|false| NoLimit[设置: 无限制模式]
    
    GetLimitType --> SwitchLimit{SWITCH节点: type值}
    SwitchLimit -->|time| TimeBranch["IF节点: value>0?"]
    SwitchLimit -->|round| RoundBranch["IF节点: value>0?"]
    SwitchLimit -->|其他| DefaultLimit[默认无限制]
    
    TimeBranch -->|true| SetTimeVar[设置变量: timeLimit=value]
    TimeBranch -->|false| SetDefaultTime[设置变量: timeLimit=180]
    
    RoundBranch -->|true| SetRoundVar[设置变量: roundLimit=value]
    RoundBranch -->|false| SetDefaultRound[设置变量: roundLimit=10]
    
    %% 挑战目标验证逻辑
    SetTimeVar & SetDefaultTime & SetRoundVar & SetDefaultRound & NoLimit & DefaultLimit --> CheckGoal{IF节点: 挑战目标!=null}
    
    CheckGoal -->|true| GetGoalType[获取: 挑战目标.type]
    CheckGoal -->|false| NoGoal[设置: 自由模式]
    
    GetGoalType --> SwitchGoal{SWITCH节点: type值}
    SwitchGoal -->|说出话语| SetKeyword["设置变量: targetKeyword=content"]
    SwitchGoal -->|做出行为| SetAction["设置变量: targetAction=content"]
    SwitchGoal -->|改变立场| SetThreshold["设置变量: targetValue=threshold"]
    SwitchGoal -->|做出判断| SetOptions["设置变量: judgeOptions=content.split('pipe')"]
    
    %% 奖励机制验证
    SetKeyword & SetAction & SetThreshold & SetOptions & NoGoal --> CheckReward{IF节点: 奖励机制!=null}
    
    CheckReward -->|true| GetRewardType[获取: 奖励机制.type]
    CheckReward -->|false| NoReward[设置: 无奖励]
    
    GetRewardType --> SwitchReward{SWITCH节点: type值}
    SwitchReward -->|解锁人设| SetCharReward["设置变量: rewardType='character'<br/>rewardContent=content"]
    SwitchReward -->|故事结局| SetStoryReward["设置变量: rewardType='story'<br/>rewardContent=content"]
    SwitchReward -->|数值达成| SetScoreReward["设置变量: rewardType='score'<br/>rewardContent=content"]
    
    SetCharReward & SetStoryReward & SetScoreReward --> ProcessReward[处理奖励数据]
    NoReward --> SetNullReward[设置变量: rewardType=null]
    
    %% 回避策略验证
    ProcessReward & SetNullReward --> CheckStrategy{"IF节点: 回避策略!=null AND 回避策略!=''"}
    
    CheckStrategy -->|true| SetStrategyVar["设置变量: aiStrategy=回避策略"]
    CheckStrategy -->|false| DefaultAI[设置变量: aiStrategy=null]
    
    SetStrategyVar & DefaultAI --> InitComplete[初始化完成]
    
    style JSONInput fill:#e1f5fe
    style CheckLimit fill:#fff3e0
    style CheckGoal fill:#fff3e0
    style CheckReward fill:#fff3e0
    style CheckStrategy fill:#fff3e0
    style SwitchLimit fill:#fce4ec
    style SwitchGoal fill:#fce4ec
```

## 4. 主循环Workflow实现

```mermaid
graph TD
    LoopStart[循环开始] --> CheckType{检查限制类型}
    
    %% 时间限制分支
    CheckType -->|时间限制| TimeCheck{检查剩余时间}
    TimeCheck -->|时间>0| ShowTimer[显示倒计时]
    TimeCheck -->|时间<=0| TimeOut[超时处理]
    
    ShowTimer --> WaitInput1[等待用户输入]
    WaitInput1 --> ProcessInput1[处理输入]
    ProcessInput1 --> CheckGoal1{检查目标达成}
    CheckGoal1 -->|达成| Success1[成功结束]
    CheckGoal1 -->|未达成| UpdateTime[更新时间]
    UpdateTime --> LoopStart
    
    %% 轮次限制分支
    CheckType -->|轮次限制| RoundCheck{检查剩余轮次}
    RoundCheck -->|轮次>0| ShowRound[显示剩余轮次]
    RoundCheck -->|轮次<=0| RoundOut[轮次用尽]
    
    ShowRound --> WaitInput2[等待用户输入]
    WaitInput2 --> ProcessInput2[处理输入]
    ProcessInput2 --> CheckGoal2{检查目标达成}
    CheckGoal2 -->|达成| Success2[成功结束]
    CheckGoal2 -->|未达成| UpdateRound[轮次-1]
    UpdateRound --> LoopStart
    
    %% 结束处理
    TimeOut --> FailureEnd[失败结束]
    RoundOut --> FailureEnd
    Success1 --> SuccessEnd[成功结束]
    Success2 --> SuccessEnd
```

## 5. 条件判断节点详细实现

```mermaid
graph LR
    subgraph IF-ELSE节点实现
        Input[输入数据] --> IfNode{IF条件节点}
        
        IfNode --> Cond1["条件: 变量==null"]
        IfNode --> Cond2["条件: 变量!=''"]
        IfNode --> Cond3["条件: 数值>阈值"]
        IfNode --> Cond4["条件: 包含关键词"]
        IfNode --> Cond5["条件: 正则匹配"]
        
        Cond1 -->|True| TrueBranch1[执行分支1]
        Cond1 -->|False| FalseBranch1[执行分支2]
        
        Cond2 -->|True| TrueBranch2[执行分支1]
        Cond2 -->|False| FalseBranch2[执行分支2]
    end
```

## 6. 运行时目标达成检测（低代码实现）

```mermaid
graph TD
    AIReply[AI回复内容] --> CheckGoalVar{IF节点: targetKeyword!=null}
    
    %% 说出话语检测分支
    CheckGoalVar -->|true| KeywordDetect{IF节点: AI回复.contains(targetKeyword)}
    CheckGoalVar -->|false| CheckActionVar{IF节点: targetAction!=null}
    
    KeywordDetect -->|true| SetSuccess1[设置变量: isSuccess=true]
    KeywordDetect -->|false| CheckActionVar
    
    %% 做出行为检测分支
    CheckActionVar -->|true| ActionDetect{正则匹配节点: 匹配targetAction}
    CheckActionVar -->|false| CheckValueVar{IF节点: targetValue!=null}
    
    ActionDetect -->|匹配| SetSuccess2[设置变量: isSuccess=true]
    ActionDetect -->|不匹配| CheckValueVar
    
    %% 改变立场检测分支
    CheckValueVar -->|true| GetCurrentVal[获取变量: currentValue]
    CheckValueVar -->|false| CheckOptionsVar{IF节点: judgeOptions!=null}
    
    GetCurrentVal --> CompareVal{IF节点: currentValue >= targetValue}
    CompareVal -->|true| SetSuccess3[设置变量: isSuccess=true]
    CompareVal -->|false| CheckOptionsVar
    
    %% 做出判断检测分支
    CheckOptionsVar -->|true| GetUserChoice[获取: 用户选择]
    CheckOptionsVar -->|false| NoCheck[无需检测]
    
    GetUserChoice --> ValidateChoice{IF节点: 选择 in judgeOptions}
    ValidateChoice -->|true| SetSuccess4[设置变量: isSuccess=true]
    ValidateChoice -->|false| NoCheck
    
    %% 汇总检测结果
    SetSuccess1 & SetSuccess2 & SetSuccess3 & SetSuccess4 --> TriggerSuccess[触发成功流程]
    NoCheck --> ContinueGame[继续游戏循环]
    
    style CheckGoalVar fill:#fff3e0
    style CheckActionVar fill:#fff3e0
    style CheckValueVar fill:#fff3e0
    style CheckOptionsVar fill:#fff3e0
    style KeywordDetect fill:#e8f5e9
    style ActionDetect fill:#e8f5e9
    style CompareVal fill:#e8f5e9
    style ValidateChoice fill:#e8f5e9
```

## 7. 实际低代码节点配置示例

```mermaid
graph LR
    subgraph IF-ELSE节点配置
        IF1["节点类型: IF-ELSE<br/>条件: config.限制条件 != null<br/>true分支: 解析限制<br/>false分支: 无限制"]
        IF2["节点类型: IF-ELSE<br/>条件: config.限制条件.type == 'time'<br/>true分支: 设置倒计时<br/>false分支: 检查轮次"]
        IF3["节点类型: IF-ELSE<br/>条件: remainTime > 0<br/>true分支: 继续游戏<br/>false分支: 超时结束"]
    end
    
    subgraph 变量赋值节点配置
        SET1["节点类型: SET_VARIABLE<br/>变量名: timeLimit<br/>值: config.限制条件.value"]
        SET2["节点类型: SET_VARIABLE<br/>变量名: targetKeyword<br/>值: config.挑战目标.content"]
        SET3["节点类型: SET_VARIABLE<br/>变量名: isSuccess<br/>值: true"]
    end
    
    subgraph SWITCH节点配置
        SW1["节点类型: SWITCH<br/>变量: config.挑战目标.type<br/>case '说出话语': 关键词分支<br/>case '做出行为': 行为分支<br/>case '改变立场': 数值分支<br/>default: 自由模式"]
    end
```

## 6. 目标检测Workflow

```mermaid
graph TD
    UserInput[用户输入] --> GetGoalType{获取目标类型}
    
    %% 说出话语检测
    GetGoalType -->|说出话语| ExtractText[提取文本]
    ExtractText --> CheckKeyword{检查关键词}
    CheckKeyword -->|包含| MarkSuccess1[标记成功]
    CheckKeyword -->|不包含| CheckSimilar{语义相似度检测}
    CheckSimilar -->|相似度>80%| MarkSuccess1
    CheckSimilar -->|相似度<80%| MarkFail1[标记失败]
    
    %% 数值检测
    GetGoalType -->|改变立场| GetCurrentValue[获取当前数值]
    GetCurrentValue --> CompareThreshold{比较阈值}
    CompareThreshold -->|>=目标值| MarkSuccess2[标记成功]
    CompareThreshold -->|<目标值| UpdateValue[更新数值]
    UpdateValue --> MarkFail2[标记失败]
    
    %% 行为检测
    GetGoalType -->|做出行为| AnalyzeBehavior[分析行为]
    AnalyzeBehavior --> CheckAction{检查动作匹配}
    CheckAction -->|匹配| MarkSuccess3[标记成功]
    CheckAction -->|不匹配| MarkFail3[标记失败]
    
    %% 判断检测
    GetGoalType -->|做出判断| GetChoice[获取选择]
    GetChoice --> ValidateChoice{验证选择}
    ValidateChoice -->|正确| MarkSuccess4[标记成功]
    ValidateChoice -->|错误| MarkFail4[标记失败]
    
    MarkSuccess1 & MarkSuccess2 & MarkSuccess3 & MarkSuccess4 --> SetSuccessFlag[设置成功标志]
    MarkFail1 & MarkFail2 & MarkFail3 & MarkFail4 --> ContinueLoop[继续循环]
```

## 7. 低代码节点类型映射

```mermaid
graph TD
    subgraph 节点类型库
        N1[变量赋值节点<br/>Set Variable]
        N2[条件判断节点<br/>IF-ELSE]
        N3[循环节点<br/>WHILE/FOR]
        N4[API调用节点<br/>HTTP Request]
        N5[数据转换节点<br/>Transform]
        N6[定时器节点<br/>Timer/Delay]
        N7[事件监听节点<br/>Event Listener]
        N8[数据存储节点<br/>Database]
        N9[消息发送节点<br/>Message]
        N10[路由节点<br/>Switch/Route]
    end
    
    subgraph 挑战系统映射
        C1[初始化] -.->|使用| N1
        C2[配置验证] -.->|使用| N2
        C3[主循环] -.->|使用| N3
        C4[AI对话] -.->|使用| N4
        C5[数据处理] -.->|使用| N5
        C6[倒计时] -.->|使用| N6
        C7[用户输入] -.->|使用| N7
        C8[保存进度] -.->|使用| N8
        C9[结果展示] -.->|使用| N9
        C10[类型路由] -.->|使用| N10
    end
```

## 8. 实际Workflow示例：时间限制挑战

```mermaid
graph TD
    Start([开始]) --> SetVar1[设置变量: timeLimit=180]
    SetVar1 --> SetVar2[设置变量: startTime=now()]
    SetVar2 --> SetVar3[设置变量: targetPhrase='我爱你']
    SetVar3 --> ShowOpening[显示: 开场白]
    
    ShowOpening --> LoopStart{循环开始}
    LoopStart --> CalcTime[计算: remainTime = timeLimit - (now - startTime)]
    CalcTime --> CheckTime{remainTime > 0?}
    
    CheckTime -->|否| ShowFail[显示: 挑战失败]
    CheckTime -->|是| ShowTime[显示: 剩余时间]
    
    ShowTime --> WaitUser[等待: 用户输入]
    WaitUser --> SaveInput[保存: userInput]
    
    SaveInput --> CallAI[调用: AI回复API]
    CallAI --> SaveAIReply[保存: aiReply]
    
    SaveAIReply --> CheckPhrase{aiReply包含targetPhrase?}
    CheckPhrase -->|是| ShowSuccess[显示: 挑战成功]
    CheckPhrase -->|否| ShowAIReply[显示: AI回复]
    
    ShowAIReply --> LoopStart
    
    ShowSuccess --> ShowReward[显示: 奖励内容]
    ShowFail --> ShowRetry[显示: 重试按钮]
    
    ShowReward --> End([结束])
    ShowRetry --> End
    
    %% 样式
    style Start fill:#90EE90
    style End fill:#FFB6C1
    style CheckTime fill:#FFE4B5
    style CheckPhrase fill:#FFE4B5
    style ShowSuccess fill:#98FB98
    style ShowFail fill:#FFA07A
```

## 9. 变量和数据流

```mermaid
graph LR
    subgraph 全局变量池
        GV1[challengeConfig]
        GV2[userProfile]
        GV3[sessionData]
        GV4[progressData]
    end
    
    subgraph 局部变量
        LV1[currentInput]
        LV2[aiResponse]
        LV3[tempResult]
        LV4[loopCounter]
    end
    
    subgraph 数据转换
        T1[JSON解析]
        T2[字符串处理]
        T3[数值计算]
        T4[布尔判断]
    end
    
    GV1 --> T1
    T1 --> LV1
    LV1 --> T2
    T2 --> LV2
    LV2 --> T3
    T3 --> LV3
    LV3 --> T4
    T4 --> GV4
```

## 10. 错误处理Workflow

```mermaid
graph TD
    Operation[执行操作] --> TryCatch{Try-Catch节点}
    
    TryCatch -->|成功| Continue[继续流程]
    TryCatch -->|错误| ErrorType{错误类型}
    
    ErrorType -->|配置错误| HandleConfig[处理配置错误]
    ErrorType -->|网络错误| HandleNetwork[处理网络错误]
    ErrorType -->|超时错误| HandleTimeout[处理超时错误]
    ErrorType -->|数据错误| HandleData[处理数据错误]
    
    HandleConfig --> LogError1[记录日志]
    HandleNetwork --> Retry{重试?}
    HandleTimeout --> LogError2[记录日志]
    HandleData --> DefaultValue[使用默认值]
    
    Retry -->|是| Operation
    Retry -->|否| LogError3[记录日志]
    
    LogError1 & LogError2 & LogError3 --> ShowUserError[显示用户友好错误]
    DefaultValue --> Continue
    ShowUserError --> Fallback[降级处理]
```

---

## 总结：低代码实现要点

### 核心节点类型需求：
1. **变量管理节点** - 设置/获取变量值
2. **条件判断节点** - IF-ELSE分支逻辑
3. **循环控制节点** - WHILE/FOR循环
4. **API调用节点** - 调用AI接口
5. **定时器节点** - 倒计时功能
6. **事件监听节点** - 用户输入监听
7. **数据转换节点** - JSON解析、字符串处理
8. **路由分发节点** - 根据类型分发流程

### 关键实现细节：
- 所有字段都通过变量存储
- 空值检测使用IF节点判断 `variable == null || variable == ""`
- 字符串匹配可用包含检测或正则表达式
- 数值比较直接使用比较运算符
- 循环使用计数器或条件控制
- 错误处理使用Try-Catch包装

这种低代码实现方式让非技术人员也能配置和修改挑战流程！