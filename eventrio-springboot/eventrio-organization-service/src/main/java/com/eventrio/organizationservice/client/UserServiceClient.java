package com.eventrio.organizationservice.client;

import com.eventrio.common.dto.OrgCountDeltaRequest;
import com.eventrio.organizationservice.config.AppConfig.UserServiceProperties;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Component
@RequiredArgsConstructor
@Slf4j
public class UserServiceClient {

    private final RestTemplate restTemplate;
    private final UserServiceProperties userServiceProperties;

    public void incrementOrgCount(String userId) {
        updateOrgCount(userId, 1);
    }

    public void decrementOrgCount(String userId) {
        updateOrgCount(userId, -1);
    }

    public String getFacebookToken(String userId) {
        String url = userServiceProperties.baseUrl() + "/api/users/" + userId + "/facebook-token";
        try {
            @SuppressWarnings("unchecked")
            Map<String, String> response = restTemplate.getForObject(url, Map.class);
            if (response == null) {
                return null;
            }
            String token = response.get("token");
            return StringUtils.hasText(token) ? token : null;
        } catch (RestClientException ex) {
            log.warn("Failed to fetch Facebook token for user {}: {}", userId, ex.getMessage());
            return null;
        }
    }

    private void updateOrgCount(String userId, int delta) {
        String url = userServiceProperties.baseUrl() + "/api/users/" + userId + "/limits/org-count";
        try {
            restTemplate.exchange(
                    url,
                    HttpMethod.PATCH,
                    new HttpEntity<>(new OrgCountDeltaRequest(delta)),
                    Map.class
            );
        } catch (RestClientException ex) {
            log.warn("Failed to update org count for user {}: {}", userId, ex.getMessage());
        }
    }
}
