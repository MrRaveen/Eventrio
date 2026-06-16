package com.eventrio.collaborationservice.service;

import com.eventrio.collaborationservice.model.Contributor;
import com.eventrio.collaborationservice.model.Organization;
import com.eventrio.collaborationservice.model.Project;
import com.eventrio.collaborationservice.model.UserAccount;
import com.eventrio.collaborationservice.repository.ContributorRepository;
import com.eventrio.collaborationservice.repository.OrganizationRepository;
import com.eventrio.collaborationservice.repository.ProjectRepository;
import com.eventrio.collaborationservice.repository.UserAccountRepository;
import com.eventrio.common.dto.CollabDashboardDto;
import com.eventrio.common.exception.ResourceNotFoundException;
import com.eventrio.common.exception.ValidationException;
import lombok.RequiredArgsConstructor;
import org.bson.types.ObjectId;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
public class CollabDashboardService {

    private final ContributorRepository contributorRepository;
    private final ProjectRepository projectRepository;
    private final OrganizationRepository organizationRepository;
    private final UserAccountRepository userAccountRepository;

    public List<CollabDashboardDto> getCollabs(String userEmail) {
        if (userEmail == null || userEmail.isBlank()) {
            throw new ValidationException("User email not found in session.");
        }

        List<Contributor> collabs = contributorRepository.findByTargetEmail(userEmail);
        List<CollabDashboardDto> response = new ArrayList<>();

        for (Contributor collab : collabs) {
            Project project = projectRepository.findById(collab.getEventID()).orElse(null);
            if (project == null) {
                continue;
            }

            Organization org = project.getOrgID() != null
                    ? organizationRepository.findById(project.getOrgID()).orElse(null)
                    : null;

            String ownerName = "Unknown Owner";
            if (project.getOwnerID() != null) {
                UserAccount owner = userAccountRepository.findBySub(project.getOwnerID()).orElse(null);
                if (owner != null && owner.getDisplayName() != null) {
                    ownerName = owner.getDisplayName();
                }
            }

            response.add(CollabDashboardDto.builder()
                    .docID(collab.getId())
                    .projectName(project.getName())
                    .projectDes(project.getDescription() != null ? project.getDescription() : "")
                    .startDate(project.getStartDate())
                    .endDate(project.getEndDate())
                    .ownerName(ownerName)
                    .orgname(org != null ? org.getOrgName() : "Unknown Organization")
                    .accept_stat(collab.isAcceptStat())
                    .eventID(collab.getEventID())
                    .orgID(collab.getOrgID())
                    .role(collab.getRole() != null ? collab.getRole() : "Unassigned")
                    .build());
        }

        return response;
    }

    public void acceptCollab(String docId, String userId) {
        if (docId == null || docId.isBlank()) {
            throw new ValidationException("Document ID is required.");
        }

        if (!ObjectId.isValid(docId.strip())) {
            throw new ValidationException("Invalid Document ID format.");
        }

        Contributor collab = contributorRepository.findById(docId.strip())
                .orElseThrow(() -> new ResourceNotFoundException("Collaboration record not found."));

        if (collab.isAcceptStat()) {
            throw new ConflictException("Collaboration is already accepted.");
        }

        collab.setAcceptStat(true);
        if (userId != null && !userId.isBlank()) {
            collab.setUserAccountID(userId);
        }

        contributorRepository.save(collab);
    }
}
