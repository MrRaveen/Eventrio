package com.eventrio.orchestrator.service;

import com.eventrio.common.enums.SagaStepStatusEnum;
import com.eventrio.orchestrator.dto.NotificationPayload;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class SagaChannelPublisher {

    private final StringRedisTemplate redisTemplate;
    private final ObjectMapper objectMapper;

    @Value("${eventrio.channel-name-orchestrator}")
    private String orchestratorChannel;

    @Value("${eventrio.notification-channel}")
    private String notificationChannel;

    public void publishStepCompletion(
            String functionName,
            SagaStepStatusEnum status,
            long elapsedMs,
            String userId,
            String workflowId,
            String projectId,
            Map<String, Object> extraPayload) {

        Map<String, Object> inner = new HashMap<>();
        inner.put("workflowID", workflowId);
        inner.put("user_id", userId);
        if (projectId != null) {
            inner.put("project_id", projectId);
        }
        if (extraPayload != null) {
            inner.putAll(extraPayload);
        }

        Map<String, Object> message = new HashMap<>();
        message.put("status", status.getValue());
        message.put("function_name", functionName);
        message.put("ms", elapsedMs);
        message.put("payload", inner);

        publish(orchestratorChannel, message);
    }

    public void publishNotification(String userId, String projectId, String workflowId) {
        NotificationPayload payload = NotificationPayload.builder()
                .userId(userId != null ? userId : "")
                .projectId(projectId != null ? projectId : "")
                .workflowId(workflowId != null ? workflowId : "")
                .build();
        try {
            publish(notificationChannel, payload);
            log.info("Published notification for user {}, project {}", userId, projectId);
        } catch (Exception ex) {
            log.error("Error publishing notification: {}", ex.getMessage());
        }
    }

    public void publishTestMessage() {
        publish(orchestratorChannel, Map.of("message", "simple"));
    }

    private void publish(String channel, Object payload) {
        try {
            redisTemplate.convertAndSend(channel, objectMapper.writeValueAsString(payload));
        } catch (Exception ex) {
            throw new IllegalStateException("Failed to publish to Redis channel " + channel, ex);
        }
    }
}
