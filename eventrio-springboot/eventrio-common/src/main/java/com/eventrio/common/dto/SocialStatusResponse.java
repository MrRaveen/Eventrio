package com.eventrio.common.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SocialStatusResponse {

    private boolean facebook;
    private boolean linkedIn;
    private boolean youtube;
    private boolean pinterest;
}
