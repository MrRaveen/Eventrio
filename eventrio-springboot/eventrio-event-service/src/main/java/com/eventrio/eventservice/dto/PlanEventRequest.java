package com.eventrio.eventservice.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PlanEventRequest {
    private String prompt;
    private String fbPageID;
    private String orgID;
}
