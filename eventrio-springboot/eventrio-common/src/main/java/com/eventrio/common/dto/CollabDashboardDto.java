package com.eventrio.common.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CollabDashboardDto {
    private String docID;
    private String projectName;
    private String projectDes;
    private Instant startDate;
    private Instant endDate;
    private String ownerName;
    private String orgname;
    private boolean accept_stat;
    private String eventID;
    private String orgID;
    private String role;
}
