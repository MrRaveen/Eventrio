package com.eventrio.orchestrator.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class NotificationPayload {

    @JsonProperty("userID")
    private String userId;

    @JsonProperty("projectID")
    private String projectId;

    @JsonProperty("workflowID")
    private String workflowId;
}
