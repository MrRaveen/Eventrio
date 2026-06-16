package com.eventrio.collaborationservice.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SendInvitationRequest {
    private String targetEmail;
    private String eventID;
    private String orgID;
    private String roleName;
}
