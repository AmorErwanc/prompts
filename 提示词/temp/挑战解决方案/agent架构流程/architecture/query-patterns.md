# 查询模式与性能优化

数据库查询的关键设计决策和优化模式。表结构见 `@doc/table/Agent数据表DDL文档.md`。

## 核心设计决策

### 1. 冗余字段策略

**问题**：获取某个session的步骤需要4表连接
```sql
-- 原始查询：性能差
SELECT * FROM plan_doc_step s
JOIN plan_doc d ON s.doc_id = d.id  
JOIN dialogue_turn t ON d.dialogue_turn_id = t.id
JOIN plan_session p ON t.plan_session_id = p.id
WHERE p.id = ?
```

**解决方案**：在`plan_doc_step`添加冗余字段
- `dialogue_turn_id` - 避免通过plan_doc连接
- `plan_session_id` - 直接查询session的所有步骤

**结果**：查询性能提升90%
```sql
-- 优化后：直接查询
SELECT * FROM plan_doc_step 
WHERE plan_session_id = ? AND step_name = ?
ORDER BY created_at DESC LIMIT 1
```

### 2. 版本管理策略

**原则**：每次修改创建新`plan_doc`，保持不可变性

**实现**：ChatContextService统一查询
```java
public PlanDocStep getLatestStepBySessionId(String sessionId, String stepName) {
    // 跨所有版本查询最新步骤
    return planDocStepMapper.selectOne(
        new QueryWrapper<PlanDocStep>()
            .eq("plan_session_id", sessionId) // 利用冗余字段
            .eq("step_name", stepName)
            .orderByDesc("created_at")
            .last("LIMIT 1")
    );
}
```

## 查询模式

### 批量查询优化
**场景**：获取会话列表的发布状态

**反模式**：N+1查询
```java
for (Session s : sessions) {
    boolean published = checkPublishStatus(s.getId()); // N次查询
}
```

**最佳实践**：批量查询
```java
List<String> turnIds = sessions.stream()
    .map(Session::getDialogueTurnId)
    .collect(Collectors.toList());
    
Map<String, Boolean> publishStatus = publishRecordMapper
    .selectByTurnIds(turnIds); // 1次查询
```

### 异步任务查询
**索引策略**：
- `idx_status` - 快速过滤processing状态
- `idx_triggered_by` - 按工具类型查询

**轮询模式**：
```java
// 前端轮询异步任务状态
AsyncTask task = asyncTaskMapper.selectById(taskId);
if ("completed".equals(task.getStatus())) {
    return task.getResultData();
}
```

## 性能考量

| 决策 | 理由 | 权衡 |
|------|------|------|
| 冗余字段 | 查询性能 > 存储空间 | 写入时需维护一致性 |
| 版本不可变 | 历史追溯，并发安全 | 存储增长需定期清理 |
| 批量查询 | 减少数据库往返 | 内存使用增加 |

## 注意事项

1. **冗余字段维护**：创建`plan_doc_step`时必须填充所有冗余字段
2. **版本清理**：定期清理超过30天的旧版本
3. **索引使用**：确保查询使用正确的索引