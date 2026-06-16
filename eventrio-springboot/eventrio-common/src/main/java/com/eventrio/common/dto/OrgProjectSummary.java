package com.eventrio.common.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class OrgProjectSummary {

    private String id;

    private String name;

    private String date;

    private String status;
}
