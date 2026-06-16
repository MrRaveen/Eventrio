package com.eventrio.common.dto;

import com.eventrio.common.enums.TaskPriority;
import com.eventrio.common.enums.TaskStatus;
import lombok.Data;

import java.time.LocalDateTime;

@Data
public class UpdateTaskRequest {

    private String title;

    private String description;

    private TaskPriority priority;

    private TaskStatus status;

    private LocalDateTime startDate;

    private LocalDateTime deadline;
}
