package com.eventrio.web.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "users")
public class UserAccount {

    @Id
    private String id;

    @Indexed(unique = true)
    private String sub;

    @Indexed(unique = true)
    private String email;

    @Builder.Default
    private boolean emailVerified = false;

    private String displayName;
    private String givenName;
    private String familyName;
    private String profilePicUrl;

    @Builder.Default
    private boolean isOnline = false;

    @Builder.Default
    private List<String> accStatus = new ArrayList<>();

    @Builder.Default
    private UserSpecificData userSpecificData = UserSpecificData.builder().build();

    @Builder.Default
    private Map<String, Object> oauthToken = new HashMap<>();
}
