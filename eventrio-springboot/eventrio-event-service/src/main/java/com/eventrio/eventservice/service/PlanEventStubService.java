package com.eventrio.eventservice.service;

import com.eventrio.common.exception.ValidationException;
import com.eventrio.eventservice.dto.AgentStubRequest;
import com.eventrio.eventservice.dto.PlanEventRequest;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
public class PlanEventStubService {

    public Map<String, String> planEventMain(PlanEventRequest request) {
        if (request.getPrompt() == null || request.getPrompt().isBlank()) {
            throw new ValidationException("Prompt required");
        }
        if (request.getOrgID() == null || request.getOrgID().isBlank()) {
            throw new ValidationException("Organization ID required");
        }

        return Map.of(
                "response",
                "Legacy AI planning has moved to the AI orchestrator. Use POST /ai/generate-event instead."
        );
    }

    public Map<String, String> createMediaStub(AgentStubRequest request) {
        return Map.of("response", "Media agent stub – connect to eventrio-ai-orchestrator-service.");
    }

    public Map<String, String> createPostsStub(AgentStubRequest request) {
        return Map.of("response", "Social media agent stub – connect to eventrio-ai-orchestrator-service.");
    }

    public Map<String, String> streamStub(AgentStubRequest request) {
        return Map.of("response", "Stream agent stub – connect to eventrio-ai-orchestrator-service.");
    }
}
