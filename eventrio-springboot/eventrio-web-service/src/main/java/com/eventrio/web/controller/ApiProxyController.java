package com.eventrio.web.controller;

import com.eventrio.web.service.ServiceClient;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.StreamUtils;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import java.nio.charset.StandardCharsets;
import java.util.Enumeration;
import java.util.Set;

@Slf4j
@RestController
@RequiredArgsConstructor
public class ApiProxyController {

    private static final Set<String> SKIP_HEADERS = Set.of(
            "host", "connection", "content-length", "transfer-encoding"
    );

    private final RestTemplate restTemplate;
    private final ServiceClient serviceClient;

    @RequestMapping({
            "/ai/**",
            "/testing/**",
            "/test-push",
            "/customer/**",
            "/payment/**",
            "/notifications/**",
            "/event-ui/**",
            "/main-dashboard/**"
    })
    public ResponseEntity<byte[]> proxy(HttpServletRequest request, HttpSession session) throws Exception {
        String path = request.getRequestURI();
        String query = request.getQueryString();
        String targetBase = resolveTargetBase(path, session);
        String rewrittenPath = rewritePath(path, session);

        String targetUrl = targetBase + rewrittenPath + (query != null ? "?" + query : "");
        HttpMethod method = HttpMethod.valueOf(request.getMethod());

        HttpHeaders headers = copyHeaders(request, session);
        byte[] body = StreamUtils.copyToByteArray(request.getInputStream());
        HttpEntity<byte[]> entity = body.length > 0
                ? new HttpEntity<>(body, headers)
                : new HttpEntity<>(headers);

        ResponseEntity<byte[]> response = restTemplate.exchange(targetUrl, method, entity, byte[].class);

        HttpHeaders responseHeaders = new HttpHeaders();
        response.getHeaders().forEach((name, values) -> {
            if (!"transfer-encoding".equalsIgnoreCase(name)) {
                responseHeaders.put(name, values);
            }
        });

        return new ResponseEntity<>(response.getBody(), responseHeaders, response.getStatusCode());
    }

    private String resolveTargetBase(String path, HttpSession session) {
        if (path.startsWith("/ai") || path.startsWith("/testing") || path.equals("/test-push")) {
            return serviceClient.orchestratorServiceUrl();
        }
        if (path.startsWith("/customer")) {
            return serviceClient.ticketingServiceUrl();
        }
        if (path.startsWith("/payment")) {
            return serviceClient.paymentServiceUrl();
        }
        if (path.startsWith("/notifications")) {
            return serviceClient.notificationServiceUrl();
        }
        if (path.startsWith("/event-ui")) {
            return serviceClient.collaborationServiceUrl();
        }
        if (path.startsWith("/main-dashboard/social-status")
                || path.startsWith("/main-dashboard/get-fb-pages")) {
            return serviceClient.userServiceUrl();
        }
        if (path.startsWith("/main-dashboard/get-list-events")
                || path.startsWith("/main-dashboard/plan-event")) {
            return serviceClient.eventServiceUrl();
        }
        if (path.startsWith("/main-dashboard/get-collabs")
                || path.startsWith("/main-dashboard/accept-collab")) {
            return serviceClient.collaborationServiceUrl();
        }
        if (path.startsWith("/main-dashboard")) {
            return serviceClient.organizationServiceUrl();
        }
        return serviceClient.orchestratorServiceUrl();
    }

    private String rewritePath(String path, HttpSession session) {
        String userId = session != null ? (String) session.getAttribute("user_id") : null;

        if ("/main-dashboard/social-status".equals(path)) {
            if (userId == null || userId.isBlank()) {
                return path;
            }
            return "/api/users/" + userId + "/social-status";
        }
        if ("/main-dashboard/get-fb-pages".equals(path)) {
            if (userId == null || userId.isBlank()) {
                return path;
            }
            return "/api/users/" + userId + "/fb-pages";
        }
        return path;
    }

    private HttpHeaders copyHeaders(HttpServletRequest request, HttpSession session) {
        HttpHeaders headers = new HttpHeaders();
        Enumeration<String> headerNames = request.getHeaderNames();
        while (headerNames.hasMoreElements()) {
            String name = headerNames.nextElement();
            if (SKIP_HEADERS.contains(name.toLowerCase())) {
                continue;
            }
            headers.add(name, request.getHeader(name));
        }

        String userId = session != null ? (String) session.getAttribute("user_id") : null;
        String userEmail = session != null ? (String) session.getAttribute("user_email") : null;
        if (userId != null && !userId.isBlank()) {
            headers.set("X-User-Id", userId);
        }
        if (userEmail != null && !userEmail.isBlank()) {
            headers.set("X-User-Email", userEmail);
        }
        if (!headers.containsKey(HttpHeaders.CONTENT_TYPE)
                && request.getContentType() != null) {
            headers.setContentType(MediaType.parseMediaType(request.getContentType()));
        }
        return headers;
    }
}
