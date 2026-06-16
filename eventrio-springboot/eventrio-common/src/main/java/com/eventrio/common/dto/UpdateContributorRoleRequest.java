package com.eventrio.common.dto;

import com.eventrio.common.enums.RolesEnum;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class UpdateContributorRoleRequest {

    @NotNull
    private RolesEnum roleName;
}
