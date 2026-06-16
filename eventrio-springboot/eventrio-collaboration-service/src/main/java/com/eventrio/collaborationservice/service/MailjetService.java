package com.eventrio.collaborationservice.service;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class MailjetService {

    private final RestTemplate restTemplate;

    @Value("${mailjet.api-url}")
    private String apiUrl;

    @Value("${mailjet.api-key-public}")
    private String apiKeyPublic;

    @Value("${mailjet.api-key-private}")
    private String apiKeyPrivate;

    @Value("${mailjet.sender-email}")
    private String senderEmail;

    @Value("${app.home-url}")
    private String appHomeUrl;

    public void sendInvitationEmail(String orgName, String projectName, String projectDesc, String targetEmail) {
        if (apiKeyPublic == null || apiKeyPublic.isBlank()
                || apiKeyPrivate == null || apiKeyPrivate.isBlank()
                || senderEmail == null || senderEmail.isBlank()) {
            throw new MailjetDeliveryException("Mailjet credentials are not configured.");
        }

        String html = generateInvitationTemplate(orgName, projectName, projectDesc, targetEmail);

        Map<String, Object> payload = Map.of(
                "Messages", List.of(
                        Map.of(
                                "From", Map.of("Email", senderEmail, "Name", "Eventrio Invitation"),
                                "To", List.of(Map.of("Email", targetEmail)),
                                "Subject", "Invitation: Join " + projectName + " on Eventrio",
                                "HTMLPart", html
                        )
                )
        );

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBasicAuth(apiKeyPublic, apiKeyPrivate, StandardCharsets.UTF_8);

        ResponseEntity<String> response = restTemplate.postForEntity(
                apiUrl,
                new HttpEntity<>(payload, headers),
                String.class
        );

        if (!response.getStatusCode().is2xxSuccessful()) {
            String details = response.getBody() != null ? response.getBody() : "Unknown Mailjet error";
            throw new MailjetDeliveryException(details);
        }
    }

    private String generateInvitationTemplate(String orgName, String projectName, String projectDesc, String targetEmail) {
        String description = projectDesc != null && !projectDesc.isBlank()
                ? projectDesc
                : "No description provided.";

        return """
                <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                    <h2>You have been invited to collaborate!</h2>
                    <p><strong>%s</strong> has invited you to join their project: <strong>%s</strong>.</p>
                    <p><strong>Project Details:</strong> %s</p>
                    <hr style="border: 1px solid #eee; margin: 20px 0;" />
                    <h3>Action Required</h3>
                    <p>To accept this invitation and access the project workspace, you must log in or create an account.</p>
                    <p style="color: #d9534f; font-weight: bold;">
                        Important: You must use this exact email address (%s) to authenticate.
                    </p>
                    <p>
                        <a href="%s" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: #fff; text-decoration: none; border-radius: 5px;">
                            Go to Dashboard
                        </a>
                    </p>
                </div>
                """.formatted(orgName, projectName, description, targetEmail, appHomeUrl);
    }
}
