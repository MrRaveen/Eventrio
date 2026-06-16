package com.eventrio.ticketingservice.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class ResendEmailService {

    private static final String RESEND_API_URL = "https://api.resend.com/emails";

    private final RestTemplate restTemplate;

    @Value("${resend.api-key:}")
    private String apiKey;

    @Value("${resend.from:Eventrio <onboarding@resend.dev>}")
    private String fromAddress;

    public Map<String, Object> sendVerificationCode(String email, String code) {
        String html = """
                <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                    <h2 style="color: #6366f1;">Eventrio Verification</h2>
                    <p>Your verification code is:</p>
                    <div style="font-size: 32px; font-weight: bold; color: #1e1b4b; letter-spacing: 4px; padding: 10px 0;">%s</div>
                    <p style="color: #666;">This code will expire in 15 minutes.</p>
                </div>
                """.formatted(code);

        return sendEmail(email, "Your Eventrio Verification Code", html);
    }

    public void sendConfirmationEmail(String email, String name, String eventName, String eventDate) {
        String html = """
                <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                    <h2 style="color: #6366f1;">Reservation Confirmed!</h2>
                    <p>Hi <strong>%s</strong>,</p>
                    <p>Your spot for <strong>%s</strong> has been successfully reserved.</p>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                    <p><strong>Event Details:</strong></p>
                    <p>📅 Date: %s</p>
                    <p>📍 Platform: Eventrio Online Portal</p>
                    <p style="font-size: 12px; color: #999; margin-top: 30px;">Thank you for using Eventrio!</p>
                </div>
                """.formatted(name, eventName, eventDate);

        try {
            sendEmail(email, "Ticket Confirmed: " + eventName, html);
        } catch (RestClientException ex) {
            log.warn("Failed to send confirmation email to {}: {}", email, ex.getMessage());
        }
    }

    private Map<String, Object> sendEmail(String to, String subject, String html) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBearerAuth(apiKey);

        Map<String, Object> body = Map.of(
                "from", fromAddress,
                "to", List.of(to),
                "subject", subject,
                "html", html
        );

        HttpEntity<Map<String, Object>> request = new HttpEntity<>(body, headers);
        ResponseEntity<Map> response = restTemplate.postForEntity(RESEND_API_URL, request, Map.class);
        return response.getBody() != null ? response.getBody() : Map.of();
    }
}
