package com.eventrio.common.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class AssignTaskRequest {

    @NotBlank
    private String userID;
}
