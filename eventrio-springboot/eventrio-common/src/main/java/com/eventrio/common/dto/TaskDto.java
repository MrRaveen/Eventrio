package com.eventrio.common.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TaskDto {
    private String id;
    private String orgID;
    private String event_id;
    private String created_by;
    private String assigned_to;
    private String title;
    private String description;
    private String priority;
    private String status;
    private Instant startDate;
    private Instant deadline;
    @Builder.Default
    private List<String> media_links = new ArrayList<>();
}
