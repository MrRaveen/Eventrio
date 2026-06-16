package com.eventrio.notificationservice.controller;

import com.eventrio.notificationservice.model.UserAccount;
import com.eventrio.notificationservice.service.RedisPublishService;
import com.eventrio.notificationservice.service.SseHubService;
import com.eventrio.notificationservice.service.UserValidationService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.Map;

@RestController
@RequiredArgsConstructor
public class StreamController {

    private static final String USER_ID_HEADER = "X-User-Id";

    private final UserValidationService userValidationService;
    private final SseHubService sseHubService;
    private final RedisPublishService redisPublishService;

    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public ResponseEntity<SseEmitter> streamGet(
            @RequestHeader(value = USER_ID_HEADER, required = false) String headerUserId,
            @RequestParam(value = "userID", required = false) String queryUserId) {

        return openUserStream(resolveUserId(headerUserId, queryUserId, null));
    }

    @PostMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public ResponseEntity<SseEmitter> streamPost(
            @RequestHeader(value = USER_ID_HEADER, required = false) String headerUserId,
            @RequestParam(value = "userID", required = false) String queryUserId,
            @RequestBody(required = false) Map<String, Object> body) {

        return openUserStream(resolveUserId(headerUserId, queryUserId, body));
    }

    @PostMapping("/notify")
    public ResponseEntity<Map<String, String>> notify(
            @RequestHeader(value = USER_ID_HEADER, required = false) String headerUserId,
            @RequestParam(value = "userID", required = false) String queryUserId,
            @RequestBody(required = false) Map<String, Object> body) {

        String userId = resolveUserId(headerUserId, queryUserId, body);
        if (userId == null || userId.isBlank()) {
            return ResponseEntity.badRequest().body(Map.of("error", "userID required"));
        }

        return userValidationService.resolveUser(userId)
                .map(user -> {
                    try {
                        redisPublishService.publish("user:" + user.getSub(), body != null ? body : Map.of());
                        return ResponseEntity.ok(Map.of("status", "ok"));
                    } catch (Exception ex) {
                        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                                .body(Map.of("error", ex.getMessage()));
                    }
                })
                .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "User not found")));
    }

    private ResponseEntity<SseEmitter> openUserStream(String userId) {
        if (userId == null || userId.isBlank()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }

        return userValidationService.resolveUser(userId)
                .map(this::createStreamResponse)
                .orElseGet(() -> ResponseEntity.status(HttpStatus.UNAUTHORIZED).build());
    }

    private ResponseEntity<SseEmitter> createStreamResponse(UserAccount user) {
        SseEmitter emitter = sseHubService.subscribe("user:" + user.getSub());
        HttpHeaders headers = new HttpHeaders();
        headers.setCacheControl("no-cache");
        headers.set("X-Accel-Buffering", "no");
        headers.setConnection("keep-alive");
        return new ResponseEntity<>(emitter, headers, HttpStatus.OK);
    }

    private String resolveUserId(String headerUserId, String queryUserId, Map<String, Object> body) {
        if (headerUserId != null && !headerUserId.isBlank()) {
            return headerUserId;
        }
        if (queryUserId != null && !queryUserId.isBlank()) {
            return queryUserId;
        }
        if (body != null && body.get("userID") != null) {
            return body.get("userID").toString();
        }
        return null;
    }
}
