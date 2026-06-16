package com.eventrio.userservice.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Limits {

    @Builder.Default
    private int orgCount = 0;

    @Builder.Default
    private int projectsCount = 0;

    @Builder.Default
    private int chatReqCount = 0;
}
