package com.eventrio.common.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class GenerateEventRequest {

    @NotBlank
    private String prompt;

    @NotBlank
    private String orgID;

    @JsonProperty("page_id")
    private String pageId;
}
