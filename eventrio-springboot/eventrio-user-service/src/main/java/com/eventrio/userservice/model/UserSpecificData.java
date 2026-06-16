package com.eventrio.userservice.model;

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
public class UserSpecificData {

    @Builder.Default
    private List<String> industry = new ArrayList<>();

    @Builder.Default
    private List<String> role = new ArrayList<>();

    @Builder.Default
    private int averageAttendeeCount = 0;

    @Builder.Default
    private int averageEventCountExcepected = 0;

    @Builder.Default
    private List<String> toolStack = new ArrayList<>();

    @Builder.Default
    private List<String> mainObjectiveOfUser = new ArrayList<>();
}
