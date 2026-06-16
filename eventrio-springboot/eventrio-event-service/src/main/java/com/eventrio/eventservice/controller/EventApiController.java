package com.eventrio.eventservice.controller;

import com.eventrio.common.dto.ApiResponse;
import com.eventrio.common.dto.BrowseEventDto;
import com.eventrio.eventservice.model.Project;
import com.eventrio.eventservice.service.EventService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/events")
@RequiredArgsConstructor
public class EventApiController {

    private final EventService eventService;

    @GetMapping("/{eventId}")
    public ResponseEntity<ApiResponse<Project>> getEvent(@PathVariable String eventId) {
        Project event = eventService.getEventById(eventId);
        return ResponseEntity.ok(ApiResponse.success("Success", event));
    }

    @GetMapping("/browse")
    public ResponseEntity<ApiResponse<List<BrowseEventDto>>> browseEvents() {
        List<BrowseEventDto> events = eventService.getBrowseEvents();
        return ResponseEntity.ok(ApiResponse.success("Success", events));
    }
}
