package com.eventrio.organizationservice.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "participants")
public class Participant {

    @Id
    private String id;

    private String name;

    @Builder.Default
    private boolean isVerifiedStat = false;

    private String email;
    private String eventID;
    private String orgID;

    @Builder.Default
    private Instant createdDate = Instant.now();
}
