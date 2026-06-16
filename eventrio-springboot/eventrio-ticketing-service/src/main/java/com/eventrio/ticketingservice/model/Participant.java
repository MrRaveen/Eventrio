package com.eventrio.ticketingservice.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.CompoundIndex;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

import java.time.Instant;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "participants")
@CompoundIndex(name = "email_event_idx", def = "{'email': 1, 'eventID': 1}")
public class Participant {

    @Id
    private String id;

    private String name;

    @Field("isVerifiedStat")
    private boolean verified;

    private String email;

    @Field("eventID")
    private String eventId;

    @Field("orgID")
    private String orgId;

    @Field("createdDate")
    private Instant createdDate;
}
