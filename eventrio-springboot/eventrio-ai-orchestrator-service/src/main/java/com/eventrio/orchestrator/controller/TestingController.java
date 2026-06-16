package com.eventrio.orchestrator.controller;

import com.eventrio.orchestrator.service.SagaEngine;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/testing")
@RequiredArgsConstructor
public class TestingController {

    private final SagaEngine sagaEngine;

    @PostMapping("/start-engine")
    public ResponseEntity<Map<String, Object>> startEngine(@RequestBody(required = false) Map<String, Object> body) {
        try {
            Map<String, Object> data = body != null ? body : Map.of();
            String userId = stringValue(data.get("userID"), "104027687086786305179");
            String orgId = stringValue(data.get("orgID"), "69f406b4eb4a9c318f5a954f");
            String prompt = stringValue(data.get("prompt"), "A test prompt for generating an awesome AI tech event in Colombo");
            String pageId = data.get("page_id") != null ? data.get("page_id").toString() : null;

            sagaEngine.startEngine(userId, prompt, orgId, pageId);

            return ResponseEntity.ok(Map.of(
                    "status", "success",
                    "message", "SAGA engine started successfully.",
                    "data_sent", Map.of(
                            "userID", userId,
                            "orgID", orgId,
                            "prompt", prompt,
                            "page_id", pageId != null ? pageId : ""
                    )
            ));
        } catch (Exception ex) {
            return ResponseEntity.internalServerError().body(Map.of(
                    "status", "error",
                    "message", ex.getMessage()
            ));
        }
    }

    private String stringValue(Object value, String defaultValue) {
        if (value == null) {
            return defaultValue;
        }
        String text = value.toString();
        return text.isBlank() ? defaultValue : text;
    }
}
