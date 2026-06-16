package com.eventrio.orchestrator.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class SagaRedisCacheService {

    private final StringRedisTemplate redisTemplate;
    private final ObjectMapper objectMapper;

    public String cacheKey(String userId, String workflowId) {
        return "saga_cache:" + userId + ":" + workflowId;
    }

    public void savePageId(String userId, String workflowId, String pageId) {
        if (pageId == null || pageId.isBlank()) {
            return;
        }
        Map<String, Object> cache = new HashMap<>();
        cache.put("page_id", pageId);
        writeCache(userId, workflowId, cache);
    }

    public void mergeExecuteWorkflowCache(String userId, String workflowId, Map<String, Object> updates) {
        Map<String, Object> existing = readCache(userId, workflowId);
        existing.putAll(updates);
        writeCache(userId, workflowId, existing);
    }

    public Map<String, Object> readCache(String userId, String workflowId) {
        try {
            String raw = redisTemplate.opsForValue().get(cacheKey(userId, workflowId));
            if (raw == null || raw.isBlank()) {
                return new HashMap<>();
            }
            return objectMapper.readValue(raw, new TypeReference<>() {});
        } catch (Exception ex) {
            log.warn("Failed to read saga cache for {}:{} – {}", userId, workflowId, ex.getMessage());
            return new HashMap<>();
        }
    }

    public String getProjectId(String userId, String workflowId) {
        Object projectId = readCache(userId, workflowId).get("projectID");
        return projectId != null ? projectId.toString() : null;
    }

    private void writeCache(String userId, String workflowId, Map<String, Object> data) {
        try {
            redisTemplate.opsForValue().set(cacheKey(userId, workflowId), objectMapper.writeValueAsString(data));
        } catch (Exception ex) {
            log.error("Failed to write saga cache for {}:{} – {}", userId, workflowId, ex.getMessage());
        }
    }
}
