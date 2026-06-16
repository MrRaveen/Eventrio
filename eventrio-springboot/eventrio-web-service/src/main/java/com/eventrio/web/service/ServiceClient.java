package com.eventrio.web.service;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

@Service
@RequiredArgsConstructor
public class ServiceClient {

    private final WebClient.Builder webClientBuilder;

    @Value("${eventrio.services.user-service}")
    private String userServiceUrl;

    @Value("${eventrio.services.organization-service}")
    private String organizationServiceUrl;

    @Value("${eventrio.services.event-service}")
    private String eventServiceUrl;

    @Value("${eventrio.services.collaboration-service}")
    private String collaborationServiceUrl;

    @Value("${eventrio.services.ticketing-service}")
    private String ticketingServiceUrl;

    @Value("${eventrio.services.payment-service}")
    private String paymentServiceUrl;

    @Value("${eventrio.services.notification-service}")
    private String notificationServiceUrl;

    @Value("${eventrio.services.orchestrator-service}")
    private String orchestratorServiceUrl;

    public WebClient userService() {
        return client(userServiceUrl);
    }

    public WebClient organizationService() {
        return client(organizationServiceUrl);
    }

    public WebClient eventService() {
        return client(eventServiceUrl);
    }

    public WebClient collaborationService() {
        return client(collaborationServiceUrl);
    }

    public WebClient ticketingService() {
        return client(ticketingServiceUrl);
    }

    public WebClient paymentService() {
        return client(paymentServiceUrl);
    }

    public WebClient notificationService() {
        return client(notificationServiceUrl);
    }

    public WebClient orchestratorService() {
        return client(orchestratorServiceUrl);
    }

    public String userServiceUrl() {
        return userServiceUrl;
    }

    public String organizationServiceUrl() {
        return organizationServiceUrl;
    }

    public String eventServiceUrl() {
        return eventServiceUrl;
    }

    public String collaborationServiceUrl() {
        return collaborationServiceUrl;
    }

    public String ticketingServiceUrl() {
        return ticketingServiceUrl;
    }

    public String paymentServiceUrl() {
        return paymentServiceUrl;
    }

    public String notificationServiceUrl() {
        return notificationServiceUrl;
    }

    public String orchestratorServiceUrl() {
        return orchestratorServiceUrl;
    }

    public HttpHeaders userHeaders(String userId, String userEmail) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        if (userId != null && !userId.isBlank()) {
            headers.set("X-User-Id", userId);
        }
        if (userEmail != null && !userEmail.isBlank()) {
            headers.set("X-User-Email", userEmail);
        }
        return headers;
    }

    private WebClient client(String baseUrl) {
        return webClientBuilder.baseUrl(baseUrl).build();
    }
}
