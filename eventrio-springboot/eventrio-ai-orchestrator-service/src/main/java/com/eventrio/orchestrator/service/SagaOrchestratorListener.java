package com.eventrio.orchestrator.service;

import com.eventrio.common.enums.SagaStepStatusEnum;
import com.eventrio.common.enums.SagaStepTypeEnum;
import com.eventrio.orchestrator.model.SagaStep;
import com.eventrio.orchestrator.repository.SagaStepRepository;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.Optional;

@Slf4j
@Component
@RequiredArgsConstructor
public class SagaOrchestratorListener {

    private final ObjectMapper objectMapper;
    private final SagaRulesService rulesService;
    private final SagaRedisCacheService cacheService;
    private final SagaStepRepository sagaStepRepository;
    private final SagaStepExecutor stepExecutor;
    private final SagaChannelPublisher channelPublisher;
    private final SagaEngine sagaEngine;

    public void onMessage(String messageBody) {
        try {
            Map<String, Object> payload = objectMapper.readValue(messageBody, new TypeReference<>() {});
            String functionName = (String) payload.get("function_name");
            if (functionName == null || functionName.isBlank()) {
                return;
            }

            updateRedisCache(functionName, payload);
            saveSagaStep(payload, functionName);

            @SuppressWarnings("unchecked")
            Map<String, Object> innerPayload = payload.get("payload") instanceof Map
                    ? (Map<String, Object>) payload.get("payload")
                    : Map.of();

            String workflowId = stringValue(innerPayload.get("workflowID"));
            String userId = stringValue(innerPayload.get("user_id"));

            Optional<String> nextStep = rulesService.findNextStep(functionName);
            if (nextStep.isPresent()) {
                dispatchNextStep(nextStep.get(), userId, workflowId);
            } else {
                log.info("Reached the end of the workflow for workflowID: {}", workflowId);
                publishCompletionNotification(userId, workflowId);
                if (workflowId != null) {
                    sagaEngine.markWorkflowCompleted(workflowId);
                }
            }
        } catch (Exception ex) {
            log.error("Error processing orchestrator message: {}", ex.getMessage(), ex);
        }
    }

    private void updateRedisCache(String functionName, Map<String, Object> payload) {
        if (!"execute_workflow".equals(functionName)) {
            return;
        }
        @SuppressWarnings("unchecked")
        Map<String, Object> inner = payload.get("payload") instanceof Map
                ? (Map<String, Object>) payload.get("payload")
                : Map.of();

        String userId = stringValue(inner.get("user_id"));
        String workflowId = stringValue(inner.get("workflowID"));
        if (userId == null || workflowId == null) {
            return;
        }

        Map<String, Object> cache = new java.util.HashMap<>();
        cache.put("userID", userId);
        cache.put("workflowID", workflowId);
        cache.put("projectID", inner.get("project_id"));
        cache.put("plan_des", inner.get("plan_des"));
        cache.put("event_name", inner.get("event_name"));
        cache.put("start_time", inner.get("start_time"));
        cache.put("end_time", inner.get("end_time"));
        cache.put("event_description", inner.get("event_description"));
        cacheService.mergeExecuteWorkflowCache(userId, workflowId, cache);
    }

    private void saveSagaStep(Map<String, Object> payload, String functionName) {
        @SuppressWarnings("unchecked")
        Map<String, Object> inner = payload.get("payload") instanceof Map
                ? (Map<String, Object>) payload.get("payload")
                : Map.of();
        String workflowId = stringValue(inner.get("workflowID"));
        if (workflowId == null) {
            return;
        }

        try {
            SagaStepTypeEnum stepType = SagaStepTypeEnum.fromValue(functionName);
            SagaStepStatusEnum stepStatus = SagaStepStatusEnum.fromValue(stringValue(payload.get("status")));
            int ms = payload.get("ms") instanceof Number n ? n.intValue() : 0;

            SagaStep step = SagaStep.builder()
                    .workflowId(workflowId)
                    .stepType(stepType)
                    .stepStatus(stepStatus)
                    .totalTimeMs(ms)
                    .responseJson(payload)
                    .build();
            sagaStepRepository.save(step);
            log.info("Saved SAGA step for workflow {}, step: {}", workflowId, functionName);
        } catch (Exception ex) {
            log.error("Error saving SAGA step: {}", ex.getMessage());
        }
    }

    private void dispatchNextStep(String nextFunctionName, String userId, String workflowId) {
        if (userId == null || workflowId == null) {
            log.warn("Missing user_id or workflow_id — cannot dispatch {}", nextFunctionName);
            return;
        }

        log.info("Dispatching next SAGA step: {} for workflow {}", nextFunctionName, workflowId);
        switch (nextFunctionName) {
            case "create_google_doc_for_event" -> stepExecutor.createGoogleDocForEvent(userId, workflowId);
            case "automate_google_meet" -> stepExecutor.automateGoogleMeet(userId, workflowId);
            case "post_image_to_facebook_page" -> stepExecutor.postImageToFacebookPage(userId, workflowId);
            case "schedule_real_google_calendar" -> stepExecutor.scheduleRealGoogleCalendar(userId, workflowId);
            default -> log.warn("No executor registered for step {}", nextFunctionName);
        }
    }

    private void publishCompletionNotification(String userId, String workflowId) {
        if (userId == null || workflowId == null) {
            return;
        }
        String projectId = cacheService.getProjectId(userId, workflowId);
        channelPublisher.publishNotification(userId, projectId, workflowId);
    }

    private String stringValue(Object value) {
        return value != null ? value.toString() : null;
    }
}
