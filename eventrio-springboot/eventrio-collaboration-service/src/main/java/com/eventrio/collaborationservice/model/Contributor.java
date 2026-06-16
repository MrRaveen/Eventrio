package com.eventrio.collaborationservice.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "contributors")
public class Contributor {

    @Id
    private String id;

    private String eventID;
    private String orgID;
    private String targetEmail;

    @Field("accept_stat")
    private boolean acceptStat;

    private String userAccountID;
    private String role;
}
