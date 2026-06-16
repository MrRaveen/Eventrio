package com.eventrio.orchestrator.controller;

import com.eventrio.common.dto.GenerateEventRequest;
import com.eventrio.orchestrator.service.GroqClientService;
import com.eventrio.orchestrator.service.SagaEngine;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/ai")
@RequiredArgsConstructor
public class AiController {

    private final SagaEngine sagaEngine;
    private final GroqClientService groqClientService;

    @PostMapping("/generate-event")
    public ResponseEntity<Map<String, String>> generateEvent(
            @RequestHeader(value = "X-User-Id", required = false) String userId,
            @Valid @RequestBody GenerateEventRequest request) {

        String resolvedUserId = StringUtils.hasText(userId) ? userId : "unknown_user";

        try {
            sagaEngine.startEngine(
                    resolvedUserId,
                    request.getPrompt(),
                    request.getOrgID(),
                    request.getPageId()
            );
            return ResponseEntity.status(HttpStatus.ACCEPTED).body(Map.of(
                    "status", "success",
                    "message", "AI event generation started. You will be notified when it completes."
            ));
        } catch (Exception ex) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Failed to start engine: " + ex.getMessage()));
        }
    }

    @PostMapping("/test-agent")
    public ResponseEntity<String> testAgent() {
        return ResponseEntity.ok(groqClientService.summarizeLatestNews());
    }
}
