package com.eventrio.orchestrator.controller;

import com.eventrio.orchestrator.service.SagaChannelPublisher;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequiredArgsConstructor
public class TestPushController {

    private final SagaChannelPublisher channelPublisher;

    @Value("${eventrio.channel-name-orchestrator}")
    private String orchestratorChannel;

    @GetMapping("/test-push")
    public ResponseEntity<Map<String, String>> testPush() {
        channelPublisher.publishTestMessage();
        return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "Pushed to channel " + orchestratorChannel
        ));
    }
}
