package com.eventrio.common.dto;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class AllCollabsResponse {

    private String docID;

    private String projectName;

    private String projectDes;

    private LocalDateTime startDate;

    private LocalDateTime endDate;

    private String ownerName;

    private String orgname;

    private boolean accept_stat;

    private String eventID;

    private String orgID;

    private String role;
}
