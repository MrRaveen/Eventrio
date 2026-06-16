package com.eventrio.web.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.ArrayList;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "organizations")
public class Organization {

    @Id
    private String id;

    private String orgName;
    private String address;
    private String createdBy;

    @Builder.Default
    private List<String> industry = new ArrayList<>();

    @Builder.Default
    private List<String> userRole = new ArrayList<>();
}
