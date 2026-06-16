package com.eventrio.organizationservice.service;

import com.eventrio.common.dto.CreateOrgRequest;
import com.eventrio.common.dto.OrgProjectSummary;
import com.eventrio.organizationservice.client.UserServiceClient;
import com.eventrio.organizationservice.exception.ResourceNotFoundException;
import com.eventrio.organizationservice.model.Organization;
import com.eventrio.organizationservice.model.Post;
import com.eventrio.organizationservice.model.Project;
import com.eventrio.organizationservice.repository.OrganizationRepository;
import com.eventrio.organizationservice.repository.ParticipantRepository;
import com.eventrio.organizationservice.repository.PostRepository;
import com.eventrio.organizationservice.repository.ProjectRepository;
import lombok.RequiredArgsConstructor;
import org.bson.types.ObjectId;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
public class OrganizationService {

    private static final DateTimeFormatter DATE_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd")
            .withZone(ZoneOffset.UTC);

    private final OrganizationRepository organizationRepository;
    private final ProjectRepository projectRepository;
    private final PostRepository postRepository;
    private final ParticipantRepository participantRepository;
    private final UserServiceClient userServiceClient;
    private final CloudinaryService cloudinaryService;
    private final FacebookPostService facebookPostService;

    public Organization createOrganization(String userId, CreateOrgRequest request) {
        Organization organization = Organization.builder()
                .orgName(request.getOrgName())
                .address(request.getAddress())
                .createdBy(userId)
                .industry(List.of(request.getIndustry().getValue()))
                .userRole(List.of(request.getUserRole().getValue()))
                .build();

        Organization saved = organizationRepository.save(organization);
        userServiceClient.incrementOrgCount(userId);
        return saved;
    }

    public Organization updateOrganization(String userId, String orgId, CreateOrgRequest request) {
        Organization organization = organizationRepository.findByIdAndCreatedBy(orgId, userId)
                .orElseThrow(() -> new ResourceNotFoundException("Organization not found or access denied"));

        organization.setOrgName(request.getOrgName());
        organization.setAddress(request.getAddress());
        organization.setIndustry(List.of(request.getIndustry().getValue()));
        organization.setUserRole(List.of(request.getUserRole().getValue()));

        return organizationRepository.save(organization);
    }

    @Transactional
    public void removeOrganization(String userId, String orgId) {
        if (!ObjectId.isValid(orgId)) {
            throw new IllegalArgumentException("Invalid organization ID format.");
        }

        Organization organization = organizationRepository.findByIdAndCreatedBy(orgId, userId)
                .orElseThrow(() -> new ResourceNotFoundException("Organization not found or access denied."));

        String fbToken = userServiceClient.getFacebookToken(userId);
        List<Project> projects = projectRepository.findByOrgID(orgId);
        List<Post> posts = postRepository.findByOrgID(orgId);

        for (Project project : projects) {
            cloudinaryService.cleanupProjectMedia(project);
        }

        facebookPostService.deletePosts(posts, fbToken);

        organizationRepository.delete(organization);
        projectRepository.deleteByOrgID(orgId);
        postRepository.deleteByOrgID(orgId);
        participantRepository.deleteByOrgID(orgId);

        userServiceClient.decrementOrgCount(userId);
    }

    public List<OrgProjectSummary> getOrgProjects(String orgId) {
        List<Project> projects = projectRepository.findByOrgID(orgId);
        List<OrgProjectSummary> summaries = new ArrayList<>();

        for (Project project : projects) {
            String date = project.getStartDate() != null
                    ? DATE_FORMAT.format(project.getStartDate())
                    : "TBD";
            String status = project.isEventStarted() ? "Started" : "Upcoming";

            summaries.add(new OrgProjectSummary(
                    project.getId(),
                    project.getName(),
                    date,
                    status
            ));
        }

        return summaries;
    }
}
