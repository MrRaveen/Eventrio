package com.eventrio.common.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class ParticipantRequest {

    @NotBlank
    private String name;

    @NotBlank
    @Email
    private String email;

    @NotBlank
    private String eventID;

    @NotBlank
    private String orgID;

    @NotBlank
    private String verificationCode;
}
