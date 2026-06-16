package com.eventrio.eventservice.service;

import com.eventrio.common.dto.BrowseEventDto;
import com.eventrio.common.dto.EventAdminDto;
import com.eventrio.common.dto.TaskDto;
import com.eventrio.common.enums.EventStatus;
import com.eventrio.common.exception.ResourceNotFoundException;
import com.eventrio.common.exception.ValidationException;
import com.eventrio.eventservice.dto.EventDashboardDataDto;
import com.eventrio.eventservice.model.Organization;
import com.eventrio.eventservice.model.Project;
import com.eventrio.eventservice.model.Task;
import com.eventrio.eventservice.repository.OrganizationRepository;
import com.eventrio.eventservice.repository.ProjectRepository;
import com.eventrio.eventservice.repository.TaskRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
@Service
@RequiredArgsConstructor
public class EventService {

    private final ProjectRepository projectRepository;
    private final OrganizationRepository organizationRepository;
    private final TaskRepository taskRepository;

    public List<EventAdminDto> getEventsForAdmin(String userId) {
        if (userId == null || userId.isBlank()) {
            throw new ValidationException("User session not found.");
        }

        List<Project> projects = projectRepository.findByOwnerID(userId);
        Instant now = Instant.now();
        List<EventAdminDto> response = new ArrayList<>();

        for (Project project : projects) {
            String orgName = organizationRepository.findById(project.getOrgID())
                    .map(Organization::getOrgName)
                    .orElse("Unknown Organization");

            Instant projectEnd = project.getEndDate() != null ? project.getEndDate() : project.getStartDate();
            EventStatus status;
            if (projectEnd != null && now.isAfter(projectEnd)) {
                status = EventStatus.COMPLETED;
            } else if (project.isEventStarted()) {
                status = EventStatus.LIVE;
            } else {
                status = EventStatus.PLANNING;
            }

            response.add(EventAdminDto.builder()
                    .eventDocID(project.getId())
                    .eventName(project.getName())
                    .isEventStarted(project.isEventStarted())
                    .organizationID(project.getOrgID() != null ? project.getOrgID() : "Unknown")
                    .organizationName(orgName)
                    .startDate(project.getStartDate())
                    .endDate(project.getEndDate() != null ? project.getEndDate() : project.getStartDate())
                    .eventStatus(status)
                    .build());
        }

        return response;
    }

    public Project getEventById(String eventId) {
        return projectRepository.findById(eventId)
                .orElseThrow(() -> new ResourceNotFoundException("Event not found"));
    }

    public List<BrowseEventDto> getBrowseEvents() {
        Instant now = Instant.now();
        List<Project> events = projectRepository
                .findByStartDateAfterAndEndDateAfterOrderByStartDateAsc(now, now);

        List<BrowseEventDto> response = new ArrayList<>();
        for (Project event : events) {
            Organization organization = event.getOrgID() != null
                    ? organizationRepository.findById(event.getOrgID()).orElse(null)
                    : null;

            String orgName = organization != null ? organization.getOrgName() : "Unknown Organization";
            String orgLocation = organization != null && organization.getAddress() != null
                    ? organization.getAddress()
                    : "Unknown Location";

            List<Map<String, String>> points = new ArrayList<>();
            if (event.getTargetingPointsToDiscuss() != null) {
                for (String point : event.getTargetingPointsToDiscuss()) {
                    Map<String, String> pointMap = new HashMap<>();
                    pointMap.put("point", point);
                    points.add(pointMap);
                }
            }

            response.add(BrowseEventDto.builder()
                    .id(event.getId())
                    .name(event.getName())
                    .description(event.getDescription())
                    .industry(event.getIndustry() != null ? event.getIndustry() : new ArrayList<>())
                    .attendeeCountExpected(event.getAttendeeCountExpected())
                    .startDate(event.getStartDate())
                    .endDate(event.getEndDate())
                    .isEventStarted(event.isEventStarted())
                    .orgName(orgName)
                    .orgID(event.getOrgID() != null ? event.getOrgID() : "")
                    .orgLocation(orgLocation)
                    .mediaLinks(event.getMediaLinks() != null ? event.getMediaLinks() : new ArrayList<>())
                    .targetingPointsToDiscuss(points)
                    .build());
        }

        return response;
    }

    public EventDashboardDataDto getEventDashboardData(String eventId) {
        Project event = getEventById(eventId);
        String scriptText = extractScriptText(event.getScriptLink());
        List<TaskDto> tasks = taskRepository.findByEventId(eventId).stream()
                .map(this::toTaskDto)
                .toList();

        return EventDashboardDataDto.builder()
                .event(event)
                .scriptText(scriptText)
                .tasks(tasks)
                .build();
    }

    private String extractScriptText(String scriptLink) {
        if (scriptLink == null || !scriptLink.startsWith("data:text/plain")) {
            return "";
        }
        String rawEncoded = scriptLink.contains(",")
                ? scriptLink.split(",", 2)[1]
                : "";
        return URLDecoder.decode(rawEncoded, StandardCharsets.UTF_8);
    }

    private TaskDto toTaskDto(Task task) {
        return TaskDto.builder()
                .id(task.getId())
                .orgID(task.getOrgID())
                .event_id(task.getEventId())
                .created_by(task.getCreated_by())
                .assigned_to(task.getAssigned_to())
                .title(task.getTitle())
                .description(task.getDescription())
                .priority(task.getPriority())
                .status(task.getStatus())
                .startDate(task.getStartDate())
                .deadline(task.getDeadline())
                .media_links(task.getMediaLinks() != null ? task.getMediaLinks() : new ArrayList<>())
                .build();
    }
}
