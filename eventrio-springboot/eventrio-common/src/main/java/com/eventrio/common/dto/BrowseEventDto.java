package com.eventrio.common.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BrowseEventDto {
    private String id;
    private String name;
    private String description;
    @Builder.Default
    private List<String> industry = new ArrayList<>();
    private int attendeeCountExpected;
    private Instant startDate;
    private Instant endDate;
    private boolean isEventStarted;
    private String orgName;
    private String orgID;
    private String orgLocation;
    @Builder.Default
    private List<String> mediaLinks = new ArrayList<>();
    @Builder.Default
    private List<Map<String, String>> targetingPointsToDiscuss = new ArrayList<>();
}
