package com.eventrio.common.dto;

import com.eventrio.common.enums.IndustryEnum;
import com.eventrio.common.enums.RoleEnum;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class CreateOrgRequest {

    private String orgName = "Unnamed Org";

    private String address = "";

    @NotNull
    private IndustryEnum industry;

    @NotNull
    private RoleEnum userRole;
}
