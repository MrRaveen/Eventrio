package com.eventrio.eventservice.model;

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
@Document(collection = "agenda")
public class Agenda {

    @Id
    private String id;

    private String eventID;

    @Builder.Default
    private List<String> agendaList = new ArrayList<>();
}
