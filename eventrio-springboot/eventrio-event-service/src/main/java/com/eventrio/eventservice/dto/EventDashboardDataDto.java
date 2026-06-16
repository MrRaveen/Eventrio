package com.eventrio.eventservice.dto;

import com.eventrio.common.dto.TaskDto;
import com.eventrio.eventservice.model.Project;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EventDashboardDataDto {
    private Project event;
    private String scriptText;
    @Builder.Default
    private List<TaskDto> tasks = new ArrayList<>();
}
