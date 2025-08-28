# TODO: Fix SSE Async Context Propagation Issue

## Problem Description
UserContext (ThreadLocal) gets cleared in `UserContextInterceptor.afterCompletion()` after SSE response returns, but async SSE processing continues in different thread pool where it needs the token for third-party API calls.

### Affected Components
- `UserContextInterceptor`: Clears context after request completion
- `InteractChatController`: SSE endpoints with @Async processing  
- `PodcastChatController`: SSE endpoints with @Async processing
- `StudioAPI`: Needs `UserContext.getToken()` for API calls
- All @Async methods in services that need user context

### Current Issue Flow
1. Request arrives → UserContextInterceptor sets ThreadLocal context
2. Controller returns SseEmitter immediately
3. UserContextInterceptor.afterCompletion() clears ThreadLocal
4. @Async method executes in different thread → UserContext.getToken() returns null
5. Third-party API calls fail due to missing Authorization header

## Recommended Solution: Spring TaskDecorator

### Implementation Steps
1. **Create ContextAwareTaskDecorator class**
```java
public class ContextAwareTaskDecorator implements TaskDecorator {
    @Override
    public Runnable decorate(Runnable runnable) {
        // Capture current context
        Map<String, String> contextMap = UserContext.getContextMap();
        String userId = UserContext.getUserId();
        String token = UserContext.getToken();
        
        return () -> {
            try {
                // Restore context in async thread
                UserContext.setUserId(userId);
                UserContext.setToken(token);
                UserContext.restoreContext(contextMap);
                
                runnable.run();
            } finally {
                // Clean up after execution
                UserContext.clear();
            }
        };
    }
}
```

2. **Update Thread Pool Configurations**
```java
@Configuration
public class AsyncConfig {
    @Bean(name = "podcastGenerationPoolExecutor")
    public TaskExecutor podcastExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setTaskDecorator(new ContextAwareTaskDecorator());
        // ... other config
        return executor;
    }
    
    @Bean(name = "interactGenerationPoolExecutor")
    public TaskExecutor interactExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setTaskDecorator(new ContextAwareTaskDecorator());
        // ... other config
        return executor;
    }
    
    @Bean(name = "asyncTaskPoolExecutor")
    public TaskExecutor asyncTaskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setTaskDecorator(new ContextAwareTaskDecorator());
        // ... other config
        return executor;
    }
}
```

3. **Enhance UserContext class**
```java
public class UserContext {
    // Add method to get full context
    public static Map<String, String> getContextMap() {
        return new HashMap<>(contextHolder.get());
    }
    
    // Add method to restore context
    public static void restoreContext(Map<String, String> context) {
        contextHolder.set(new HashMap<>(context));
    }
}
```

## Alternative Solutions (Not Recommended)

### Solution 1: Pass Context Explicitly
- **Pros**: Simple, explicit control
- **Cons**: Requires changing many method signatures, verbose

### Solution 2: Request-Scoped Bean
- **Pros**: Spring-native approach
- **Cons**: Complex configuration, potential proxy issues

### Solution 3: MDC Pattern
- **Pros**: Good for logging
- **Cons**: Requires replacing UserContext entirely

### Solution 4: Context Snapshot
- **Pros**: Immutable, thread-safe
- **Cons**: More complex than TaskDecorator

## Testing Requirements
1. Verify token is available in async threads
2. Test concurrent requests don't interfere with each other
3. Ensure proper cleanup after execution
4. Test with multiple simultaneous SSE connections
5. Verify memory leak prevention (ThreadLocal cleanup)

## Priority
**HIGH** - This issue prevents SSE endpoints from calling third-party APIs in production

## Estimated Effort
- Implementation: 2-3 hours
- Testing: 2 hours
- Total: 4-5 hours

## Files to Modify
1. Create: `src/main/java/com/agent/config/ContextAwareTaskDecorator.java`
2. Modify: `src/main/java/com/agent/config/AsyncConfig.java` (or wherever thread pools are configured)
3. Modify: `src/main/java/com/agent/aop/interceptor/UserContext.java`
4. Test files for affected services

## Notes
- This is a common pattern in Spring applications with async processing
- TaskDecorator is the standard Spring solution for ThreadLocal propagation
- Alternative: Spring Security has similar context propagation mechanisms that could be referenced