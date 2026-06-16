package com.eventrio.eventservice.controller;

import com.eventrio.common.dto.ApiResponse;
import com.eventrio.common.dto.BrowseEventDto;
import com.eventrio.common.dto.EventAdminDto;
import com.eventrio.common.exception.ValidationException;
import com.eventrio.eventservice.dto.AgentStubRequest;
import com.eventrio.eventservice.dto.EventDashboardDataDto;
import com.eventrio.eventservice.dto.PlanEventRequest;
import com.eventrio.eventservice.model.Project;
import com.eventrio.eventservice.service.EventService;
import com.eventrio.eventservice.service.PlanEventStubService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/main-dashboard")
@RequiredArgsConstructor
public class MainDashboardController {

    private final EventService eventService;
    private final PlanEventStubService planEventStubService;

    @GetMapping("/get-list-events")
    public ResponseEntity<?> getListEvents(
            @RequestHeader(value = "X-User-Id", required = false) String userId) {
        if (userId == null || userId.isBlank()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(ApiResponse.fail("Unauthorized", "User session not found."));
        }

        List<EventAdminDto> events = eventService.getEventsForAdmin(userId);
        return ResponseEntity.ok(ApiResponse.success("Success", events));
    }

    @PostMapping("/plan-event/main")
    public ResponseEntity<Map<String, String>> planEventMain(@RequestBody PlanEventRequest request) {
        try {
            return ResponseEntity.ok(planEventStubService.planEventMain(request));
        } catch (ValidationException ex) {
            return ResponseEntity.badRequest().body(Map.of("error", ex.getMessage()));
        }
    }

    @PostMapping("/plan-event/create-media")
    public ResponseEntity<Map<String, String>> createMedia(@RequestBody(required = false) AgentStubRequest request) {
        return ResponseEntity.ok(planEventStubService.createMediaStub(request));
    }

    @PostMapping("/plan-event/create-posts")
    public ResponseEntity<Map<String, String>> createPosts(@RequestBody(required = false) AgentStubRequest request) {
        return ResponseEntity.ok(planEventStubService.createPostsStub(request));
    }

    @PostMapping("/plan-event/stream")
    public ResponseEntity<Map<String, String>> stream(@RequestBody(required = false) AgentStubRequest request) {
        return ResponseEntity.ok(planEventStubService.streamStub(request));
    }
}
