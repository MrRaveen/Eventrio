package com.eventrio.collaborationservice.service;

import com.eventrio.collaborationservice.dto.SendInvitationRequest;
import com.eventrio.collaborationservice.model.Contributor;
import com.eventrio.collaborationservice.model.Organization;
import com.eventrio.collaborationservice.model.Project;
import com.eventrio.collaborationservice.repository.ContributorRepository;
import com.eventrio.collaborationservice.repository.OrganizationRepository;
import com.eventrio.collaborationservice.repository.ProjectRepository;
import com.eventrio.common.dto.ContributorDto;
import com.eventrio.common.enums.CollaboratorRole;
import com.eventrio.common.exception.ResourceNotFoundException;
import com.eventrio.common.exception.ValidationException;
import lombok.RequiredArgsConstructor;
import org.bson.types.ObjectId;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

@Service
@RequiredArgsConstructor
public class ContributorService {

    private final ContributorRepository contributorRepository;
    private final ProjectRepository projectRepository;
    private final OrganizationRepository organizationRepository;
    private final MailjetService mailjetService;

    public List<String> getRoles() {
        return Arrays.stream(CollaboratorRole.values())
                .map(CollaboratorRole::getValue)
                .toList();
    }

    public List<String> getMedia(String eventId) {
        if (eventId == null || eventId.isBlank()) {
            throw new ResourceNotFoundException("Event ID is null");
        }

        Project project = projectRepository.findById(eventId)
                .orElseThrow(() -> new ResourceNotFoundException("Event is not found"));

        return project.getMediaLinks() != null ? project.getMediaLinks() : new ArrayList<>();
    }

    public List<ContributorDto> viewContributors(String eventId) {
        if (eventId == null || eventId.isBlank()) {
            throw new ValidationException("Event ID cannot be empty.");
        }

        return contributorRepository.findByEventID(eventId.strip()).stream()
                .map(this::toDto)
                .toList();
    }

    public void updateContributorRole(String docId, String roleName) {
        if (roleName == null || roleName.isBlank()) {
            throw new ValidationException("Missing required field: 'roleName' in JSON payload.");
        }

        CollaboratorRole validRole;
        try {
            validRole = CollaboratorRole.fromValue(roleName);
        } catch (IllegalArgumentException ex) {
            throw new ValidationException(
                    "Invalid roleName. Allowed values are: " + getRoles()
            );
        }

        Contributor contributor = findContributorById(docId);
        contributor.setRole(validRole.getValue());
        contributorRepository.save(contributor);
    }

    public void sendInvitation(SendInvitationRequest request) {
        if (request == null) {
            throw new ValidationException("Missing JSON payload.");
        }

        String targetEmail = request.getTargetEmail();
        String eventId = request.getEventID();
        String orgId = request.getOrgID();
        String roleName = request.getRoleName();

        if (targetEmail == null || targetEmail.isBlank()
                || eventId == null || eventId.isBlank()
                || orgId == null || orgId.isBlank()
                || roleName == null || roleName.isBlank()) {
            throw new ValidationException(
                    "Missing required fields: targetEmail, eventID, orgID, and roleName are mandatory."
            );
        }

        CollaboratorRole validRole;
        try {
            validRole = CollaboratorRole.fromValue(roleName);
        } catch (IllegalArgumentException ex) {
            throw new ValidationException(
                    "Invalid roleName. Allowed values are: " + getRoles()
            );
        }

        if (!targetEmail.toLowerCase().endsWith("@gmail.com")) {
            throw new ValidationException("Only Google email addresses (@gmail.com) are permitted.");
        }

        Organization organization = organizationRepository.findById(orgId)
                .orElseThrow(() -> new ResourceNotFoundException("Invalid Organization or Project ID."));
        Project project = projectRepository.findById(eventId)
                .orElseThrow(() -> new ResourceNotFoundException("Invalid Organization or Project ID."));

        if (contributorRepository.existsByTargetEmailAndEventID(targetEmail, eventId)) {
            throw new ConflictException("User has already been added to this project.");
        }

        Contributor contributor = Contributor.builder()
                .eventID(eventId)
                .orgID(orgId)
                .targetEmail(targetEmail)
                .role(validRole.getValue())
                .acceptStat(false)
                .build();

        contributor = contributorRepository.save(contributor);

        try {
            mailjetService.sendInvitationEmail(
                    organization.getOrgName(),
                    project.getName(),
                    project.getDescription(),
                    targetEmail
            );
        } catch (MailjetDeliveryException ex) {
            contributorRepository.delete(contributor);
            throw ex;
        }
    }

    public void removeContributor(String docId) {
        if (docId == null || docId.isBlank()) {
            throw new ValidationException("Document ID is required.");
        }

        Contributor contributor = findContributorById(docId.strip());
        contributorRepository.delete(contributor);
    }

    private Contributor findContributorById(String docId) {
        validateObjectId(docId);
        return contributorRepository.findById(docId.strip())
                .orElseThrow(() -> new ResourceNotFoundException("Contributor not found for the provided Document ID."));
    }

    private ContributorDto toDto(Contributor contributor) {
        return ContributorDto.builder()
                .id(contributor.getId())
                .eventID(contributor.getEventID())
                .orgID(contributor.getOrgID())
                .targetEmail(contributor.getTargetEmail())
                .accept_stat(contributor.isAcceptStat())
                .role(contributor.getRole())
                .userAccountID(contributor.getUserAccountID() != null
                        ? contributor.getUserAccountID()
                        : "Pending Registration")
                .build();
    }

    private void validateObjectId(String docId) {
        if (!ObjectId.isValid(docId)) {
            throw new ValidationException("Invalid Document ID format.");
        }
    }
}
