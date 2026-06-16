package com.eventrio.userservice.service;

import com.eventrio.userservice.config.AppConfig.FacebookProperties;
import com.eventrio.userservice.exception.ResourceNotFoundException;
import com.eventrio.userservice.repository.UserRepository;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.net.URI;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class FacebookOAuthService {

    private static final String FB_GRAPH_VERSION = "v19.0";
    private static final String SESSION_USER_KEY = "user_id";

    private final FacebookProperties facebookProperties;
    private final UserService userService;
    private final UserRepository userRepository;
    private final RestTemplate restTemplate;

    public URI buildAuthorizationRedirect(HttpSession session) {
        if (!StringUtils.hasText(facebookProperties.appId())) {
            throw new IllegalStateException("Facebook App ID not configured.");
        }

        String userId = session != null ? (String) session.getAttribute(SESSION_USER_KEY) : null;
        String scopes = "pages_show_list,pages_manage_posts,pages_read_engagement";

        return UriComponentsBuilder
                .fromHttpUrl("https://www.facebook.com/" + FB_GRAPH_VERSION + "/dialog/oauth")
                .queryParam("client_id", facebookProperties.appId())
                .queryParam("redirect_uri", facebookProperties.redirectUri())
                .queryParam("scope", scopes)
                .queryParam("state", userId != null ? userId : "")
                .build(true)
                .toUri();
    }

    public URI handleCallback(String code, String state, HttpSession session) {
        if (!StringUtils.hasText(code)) {
            throw new IllegalArgumentException("Authorization failed");
        }

        String shortLivedToken = exchangeCodeForToken(code);
        String longLivedToken = exchangeForLongLivedToken(shortLivedToken);

        String userId = session != null ? (String) session.getAttribute(SESSION_USER_KEY) : null;
        if (!StringUtils.hasText(userId)) {
            userId = state;
        }

        if (!StringUtils.hasText(userId) || userRepository.findBySub(userId).isEmpty()) {
            throw new ResourceNotFoundException("User not found for Facebook callback");
        }

        userService.saveFacebookToken(userId, longLivedToken);
        return URI.create(facebookProperties.successRedirectUri());
    }

    public void bindSessionUser(HttpSession session, String userId) {
        if (session != null && StringUtils.hasText(userId)) {
            session.setAttribute(SESSION_USER_KEY, userId);
        }
    }

    @SuppressWarnings("unchecked")
    private String exchangeCodeForToken(String code) {
        String url = String.format(
                "https://graph.facebook.com/%s/oauth/access_token?client_id=%s&redirect_uri=%s&client_secret=%s&code=%s",
                FB_GRAPH_VERSION,
                facebookProperties.appId(),
                facebookProperties.redirectUri(),
                facebookProperties.appSecret(),
                code
        );

        try {
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);
            if (response == null || !response.containsKey("access_token")) {
                String message = extractErrorMessage(response);
                throw new IllegalArgumentException("Failed to obtain user access token: " + message);
            }
            return String.valueOf(response.get("access_token"));
        } catch (RestClientException ex) {
            throw new IllegalStateException("Request to Meta API failed: " + ex.getMessage(), ex);
        }
    }

    @SuppressWarnings("unchecked")
    private String exchangeForLongLivedToken(String shortLivedToken) {
        String url = String.format(
                "https://graph.facebook.com/%s/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s",
                FB_GRAPH_VERSION,
                facebookProperties.appId(),
                facebookProperties.appSecret(),
                shortLivedToken
        );

        Map<String, Object> response = restTemplate.getForObject(url, Map.class);
        if (response == null || !response.containsKey("access_token")) {
            String message = extractErrorMessage(response);
            throw new IllegalArgumentException("Failed to obtain long-lived token: " + message);
        }
        return String.valueOf(response.get("access_token"));
    }

    @SuppressWarnings("unchecked")
    private String extractErrorMessage(Map<String, Object> response) {
        if (response == null) {
            return "Unknown error";
        }
        Object error = response.get("error");
        if (error instanceof Map<?, ?> errorMap) {
            Object message = errorMap.get("message");
            if (message != null) {
                return message.toString();
            }
        }
        return "Unknown error";
    }
}
