package com.eventrio.organizationservice.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "projects")
public class Project {

    @Id
    private String id;

    private String name;
    private String description;

    @Builder.Default
    private List<String> industry = new ArrayList<>();

    @Builder.Default
    private List<String> userRole = new ArrayList<>();

    @Builder.Default
    private int attendeeCountExpected = 0;

    private Instant startDate;
    private Instant endDate;
    private String eventPlan;
    private String fb_post;

    @Builder.Default
    private boolean isEventStarted = false;

    private String orgID;
    private String ownerID;

    @Builder.Default
    private List<String> mediaLinks = new ArrayList<>();

    @Builder.Default
    private List<String> targetingPointsToDiscuss = new ArrayList<>();

    @Builder.Default
    private String meetingUrl = "";

    private String slideShowLink;
    private String scriptLink;
}
