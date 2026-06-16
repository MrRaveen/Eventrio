package com.eventrio.organizationservice.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.mongodb.MongoDatabaseFactory;
import org.springframework.data.mongodb.MongoTransactionManager;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class AppConfig {

    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }

    @Bean
    public WebClient webClient() {
        return WebClient.builder().build();
    }

    @Bean
    public MongoTransactionManager transactionManager(MongoDatabaseFactory dbFactory) {
        return new MongoTransactionManager(dbFactory);
    }

    @Bean
    public CloudinaryProperties cloudinaryProperties(
            @Value("${eventrio.cloudinary.cloud-name}") String cloudName,
            @Value("${eventrio.cloudinary.api-key}") String apiKey,
            @Value("${eventrio.cloudinary.api-secret}") String apiSecret) {
        return new CloudinaryProperties(cloudName, apiKey, apiSecret);
    }

    @Bean
    public UserServiceProperties userServiceProperties(
            @Value("${eventrio.user-service.base-url}") String baseUrl) {
        return new UserServiceProperties(baseUrl);
    }

    public record CloudinaryProperties(String cloudName, String apiKey, String apiSecret) {
    }

    public record UserServiceProperties(String baseUrl) {
    }
}
