package com.eventrio.web.service;

import com.eventrio.common.dto.BrowseEventDto;
import com.eventrio.web.model.Organization;
import com.eventrio.web.model.Project;
import com.eventrio.web.model.Task;
import com.eventrio.web.repository.OrganizationRepository;
import com.eventrio.web.repository.ProjectRepository;
import com.eventrio.web.repository.TaskRepository;
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
public class UiDataService {

    private final OrganizationRepository organizationRepository;
    private final ProjectRepository projectRepository;
    private final TaskRepository taskRepository;

    public List<Map<String, Object>> getOrganizationsForUser(String userId) {
        List<Map<String, Object>> orgs = new ArrayList<>();
        for (Organization org : organizationRepository.findByCreatedBy(userId)) {
            Map<String, Object> row = new HashMap<>();
            row.put("id", org.getId());
            row.put("orgName", org.getOrgName());
            row.put("address", org.getAddress());
            row.put("industry", org.getIndustry() != null && !org.getIndustry().isEmpty()
                    ? org.getIndustry().get(0) : "General");
            row.put("userRole", org.getUserRole() != null && !org.getUserRole().isEmpty()
                    ? org.getUserRole().get(0) : "member");
            orgs.add(row);
        }
        return orgs;
    }

    public Project getEventOrThrow(String eventId) {
        return projectRepository.findById(eventId)
                .orElseThrow(() -> new IllegalArgumentException("Event not found"));
    }

    public String extractScriptText(Project event) {
        if (event.getScriptLink() == null || !event.getScriptLink().startsWith("data:text/plain")) {
            return "";
        }
        String rawEncoded = event.getScriptLink().split(",", 2)[1];
        return URLDecoder.decode(rawEncoded, StandardCharsets.UTF_8);
    }

    public List<Task> getEventTasks(String eventId) {
        return taskRepository.findByEventId(eventId);
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

            List<Map<String, String>> points = new ArrayList<>();
            if (event.getTargetingPointsToDiscuss() != null) {
                for (String point : event.getTargetingPointsToDiscuss()) {
                    points.add(Map.of("point", point));
                }
            }

            response.add(BrowseEventDto.builder()
                    .id(event.getId())
                    .name(event.getName())
                    .description(event.getDescription())
                    .industry(event.getIndustry())
                    .attendeeCountExpected(event.getAttendeeCountExpected())
                    .startDate(event.getStartDate())
                    .endDate(event.getEndDate())
                    .isEventStarted(event.isEventStarted())
                    .orgName(organization != null ? organization.getOrgName() : "Unknown Organization")
                    .orgID(event.getOrgID() != null ? event.getOrgID() : "")
                    .orgLocation(organization != null && organization.getAddress() != null
                            ? organization.getAddress() : "Unknown Location")
                    .mediaLinks(event.getMediaLinks())
                    .targetingPointsToDiscuss(points)
                    .build());
        }
        return response;
    }
}
