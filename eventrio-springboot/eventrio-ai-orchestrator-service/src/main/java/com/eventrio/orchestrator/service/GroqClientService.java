package com.eventrio.orchestrator.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class GroqClientService {

    private final WebClient groqWebClient;

    public String summarizeLatestNews() {
        Map<String, Object> body = Map.of(
                "model", "llama-3.1-8b-instant",
                "messages", List.of(
                        Map.of("role", "user", "content", "Summarise the latest news in 3 bullet points")
                )
        );

        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> response = groqWebClient.post()
                    .uri("/chat/completions")
                    .bodyValue(body)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .onErrorResume(ex -> Mono.just(Map.of("error", ex.getMessage())))
                    .block();

            if (response == null) {
                return "No response from Groq API";
            }
            if (response.containsKey("error")) {
                return response.get("error").toString();
            }

            @SuppressWarnings("unchecked")
            List<Map<String, Object>> choices = (List<Map<String, Object>>) response.get("choices");
            if (choices == null || choices.isEmpty()) {
                return response.toString();
            }

            @SuppressWarnings("unchecked")
            Map<String, Object> message = (Map<String, Object>) choices.get(0).get("message");
            return message != null ? message.get("content").toString() : response.toString();
        } catch (Exception ex) {
            log.error("Groq API call failed: {}", ex.getMessage());
            return ex.getMessage();
        }
    }
}
