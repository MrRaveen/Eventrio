package com.eventrio.common.dto;

import com.eventrio.common.enums.IndustryEnum;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Data
public class ProjectBrowseResponse {

    private String id;

    private String name;

    private String description;

    private List<IndustryEnum> industry = new ArrayList<>();

    private int attendeeCountExpected;

    private LocalDateTime startDate;

    private LocalDateTime endDate;

    private boolean isEventStarted;

    private String orgName;

    private String orgID;

    private String orgLocation;

    private List<String> mediaLinks = new ArrayList<>();

    private List<TargetingPoint> targetingPointsToDiscuss = new ArrayList<>();

    @Data
    public static class TargetingPoint {

        private String point;
    }
}
