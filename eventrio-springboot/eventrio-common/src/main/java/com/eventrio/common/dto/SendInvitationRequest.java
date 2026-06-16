package com.eventrio.common.dto;

import com.eventrio.common.enums.RolesEnum;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class SendInvitationRequest {

    @NotBlank
    @Email
    private String targetEmail;

    @NotBlank
    private String eventID;

    @NotBlank
    private String orgID;

    @NotNull
    private RolesEnum roleName;
}
