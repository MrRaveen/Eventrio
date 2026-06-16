package com.eventrio.common.dto;

import com.eventrio.common.enums.EventStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EventAdminDto {
    private String eventDocID;
    private String eventName;
    private boolean isEventStarted;
    private String organizationID;
    private String organizationName;
    private Instant startDate;
    private Instant endDate;
    private EventStatus eventStatus;
}
