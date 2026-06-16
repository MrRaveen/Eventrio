package com.eventrio.userservice.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

@Configuration
public class AppConfig {

    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }

    @Bean
    public FacebookProperties facebookProperties(
            @Value("${eventrio.facebook.app-id}") String appId,
            @Value("${eventrio.facebook.app-secret}") String appSecret,
            @Value("${eventrio.facebook.redirect-uri}") String redirectUri,
            @Value("${eventrio.facebook.success-redirect-uri}") String successRedirectUri) {
        return new FacebookProperties(appId, appSecret, redirectUri, successRedirectUri);
    }

    public record FacebookProperties(
            String appId,
            String appSecret,
            String redirectUri,
            String successRedirectUri) {
    }
}
