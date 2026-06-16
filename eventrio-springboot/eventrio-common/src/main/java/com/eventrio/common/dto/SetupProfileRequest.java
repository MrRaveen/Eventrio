package com.eventrio.common.dto;

import com.eventrio.common.enums.IndustryEnum;
import com.eventrio.common.enums.ObjectiveEnum;
import com.eventrio.common.enums.RoleEnum;
import com.eventrio.common.enums.ToolStackEnum;
import jakarta.validation.constraints.Min;
import lombok.Data;

import java.util.ArrayList;
import java.util.List;

@Data
public class SetupProfileRequest {

    private List<IndustryEnum> industry = new ArrayList<>();

    private List<RoleEnum> role = new ArrayList<>();

    @Min(0)
    private int averageAttendeeCount = 0;

    @Min(0)
    private int averageEventCountExcepected = 0;

    private List<ToolStackEnum> toolStack = new ArrayList<>();

    private List<ObjectiveEnum> mainObjectiveOfUser = new ArrayList<>();
}
