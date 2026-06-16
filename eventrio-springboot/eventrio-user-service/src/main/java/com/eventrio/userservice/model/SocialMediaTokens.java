package com.eventrio.userservice.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SocialMediaTokens {

    @Builder.Default
    private String facebook = "";

    @Builder.Default
    private String linkedIn = "";

    @Builder.Default
    private String pinterest = "";

    @Builder.Default
    private String youtube = "";
}
