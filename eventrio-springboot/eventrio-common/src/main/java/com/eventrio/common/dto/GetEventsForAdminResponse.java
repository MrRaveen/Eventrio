package com.eventrio.common.dto;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class GetEventsForAdminResponse {

    private String eventDocID;

    private String eventName;

    private boolean isEventStarted;

    private String organizationID;

    private String organizationName;

    private LocalDateTime startDate;

    private LocalDateTime endDate;

    private String eventStatus;
}
