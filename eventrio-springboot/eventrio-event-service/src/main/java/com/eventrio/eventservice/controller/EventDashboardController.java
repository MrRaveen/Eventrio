package com.eventrio.eventservice.controller;

import com.eventrio.common.dto.ApiResponse;
import com.eventrio.eventservice.dto.EventDashboardDataDto;
import com.eventrio.eventservice.service.EventService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/event-dashboard")
@RequiredArgsConstructor
public class EventDashboardController {

    private final EventService eventService;

    @GetMapping("/{eventId}/data")
    public ResponseEntity<ApiResponse<EventDashboardDataDto>> getEventDashboardData(
            @PathVariable String eventId) {
        EventDashboardDataDto data = eventService.getEventDashboardData(eventId);
        return ResponseEntity.ok(ApiResponse.success("Success", data));
    }
}
