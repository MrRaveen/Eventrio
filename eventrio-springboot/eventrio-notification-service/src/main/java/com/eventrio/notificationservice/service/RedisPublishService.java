package com.eventrio.notificationservice.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class RedisPublishService {

    private final StringRedisTemplate redisTemplate;
    private final ObjectMapper objectMapper;

    public void publish(String channel, Map<String, Object> payload) throws JsonProcessingException {
        redisTemplate.convertAndSend(channel, objectMapper.writeValueAsString(payload));
    }

    public void publishRaw(String channel, String payload) {
        redisTemplate.convertAndSend(channel, payload);
    }
}
