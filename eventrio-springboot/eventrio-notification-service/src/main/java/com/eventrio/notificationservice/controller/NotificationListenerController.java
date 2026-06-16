package com.eventrio.notificationservice.controller;

import com.eventrio.notificationservice.model.UserAccount;
import com.eventrio.notificationservice.service.SseHubService;
import com.eventrio.notificationservice.service.UserValidationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@Slf4j
@RestController
@RequestMapping("/notifications")
@RequiredArgsConstructor
public class NotificationListenerController {

    private static final String USER_ID_HEADER = "X-User-Id";

    private final UserValidationService userValidationService;
    private final SseHubService sseHubService;

    @Value("${notification.channel}")
    private String notificationChannel;

    @GetMapping(value = "/listen", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public ResponseEntity<SseEmitter> listen(
            @RequestHeader(value = USER_ID_HEADER, required = false) String headerUserId,
            @RequestParam(value = "userID", required = false) String queryUserId) {

        String userId = headerUserId != null && !headerUserId.isBlank() ? headerUserId : queryUserId;
        if (userId == null || userId.isBlank()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }

        return userValidationService.resolveUser(userId)
                .map(user -> createFilteredStream(user, userId))
                .orElseGet(() -> ResponseEntity.status(HttpStatus.UNAUTHORIZED).build());
    }

    private ResponseEntity<SseEmitter> createFilteredStream(UserAccount user, String sessionUserId) {
        log.info("User '{}' connected to notification stream on channel '{}'", sessionUserId, notificationChannel);

        SseEmitter emitter = sseHubService.subscribe(
                notificationChannel,
                sseHubService.userIdFilter(user.getSub())
        );

        HttpHeaders headers = new HttpHeaders();
        headers.setCacheControl("no-cache");
        headers.set("X-Accel-Buffering", "no");
        headers.setConnection("keep-alive");
        return new ResponseEntity<>(emitter, headers, HttpStatus.OK);
    }
}
