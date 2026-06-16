package com.eventrio.eventservice.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

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

    @Field("userRole")
    @Builder.Default
    private List<String> userRole = new ArrayList<>();

    private int attendeeCountExpected;
    private Instant startDate;
    private Instant endDate;
    private String eventPlan;
    private String fb_post;
    private boolean isEventStarted;
    private String orgID;
    private String ownerID;

    @Builder.Default
    private List<String> mediaLinks = new ArrayList<>();

    @Builder.Default
    private List<String> targetingPointsToDiscuss = new ArrayList<>();

    private String meetingUrl;
    private String slideShowLink;
    private String scriptLink;
}
