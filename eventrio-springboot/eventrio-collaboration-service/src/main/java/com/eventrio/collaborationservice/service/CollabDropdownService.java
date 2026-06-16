package com.eventrio.collaborationservice.service;

import com.eventrio.collaborationservice.model.Contributor;
import com.eventrio.collaborationservice.model.UserAccount;
import com.eventrio.collaborationservice.repository.ContributorRepository;
import com.eventrio.collaborationservice.repository.UserAccountRepository;
import com.eventrio.common.dto.CollabDropdownDto;
import com.eventrio.common.exception.ValidationException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
public class CollabDropdownService {

    private final ContributorRepository contributorRepository;
    private final UserAccountRepository userAccountRepository;

    public List<CollabDropdownDto> getCollabsDropdown(String eventId) {
        if (eventId == null || eventId.isBlank()) {
            throw new ValidationException("Event ID is required.");
        }

        List<Contributor> contributors = contributorRepository.findByEventID(eventId.strip());
        List<CollabDropdownDto> response = new ArrayList<>();

        for (Contributor contributor : contributors) {
            String personName = "";
            String userAccId = contributor.getUserAccountID() != null ? contributor.getUserAccountID() : "";
            String status = contributor.isAcceptStat() ? "Accepted" : "Pending";

            if (contributor.isAcceptStat() && contributor.getUserAccountID() != null) {
                UserAccount user = userAccountRepository.findBySub(contributor.getUserAccountID()).orElse(null);
                if (user != null) {
                    if (user.getDisplayName() != null && !user.getDisplayName().isBlank()) {
                        personName = user.getDisplayName();
                    } else {
                        String given = user.getGivenName() != null ? user.getGivenName() : "";
                        String family = user.getFamilyName() != null ? user.getFamilyName() : "";
                        personName = (given + " " + family).trim();
                    }
                }
            }

            response.add(CollabDropdownDto.builder()
                    .docID(contributor.getId())
                    .userAccID(userAccId)
                    .personName(personName)
                    .status(status)
                    .email(contributor.getTargetEmail())
                    .build());
        }

        return response;
    }
}
