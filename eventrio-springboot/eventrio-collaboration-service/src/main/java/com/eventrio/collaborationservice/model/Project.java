package com.eventrio.collaborationservice.model;

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
    private Instant startDate;
    private Instant endDate;
    private String orgID;
    private String ownerID;

    @Builder.Default
    private java.util.List<String> mediaLinks = new java.util.ArrayList<>();
}
