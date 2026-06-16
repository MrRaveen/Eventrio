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
@Document(collection = "tasks")
public class Task {

    @Id
    private String id;

    private String orgID;

    @Field("event_id")
    private String eventId;

    private String created_by;
    private String assigned_to;
    private String title;
    private String description;
    private String priority;
    private String status;
    private Instant startDate;
    private Instant deadline;

    @Field("media_links")
    @Builder.Default
    private List<String> mediaLinks = new ArrayList<>();
}
