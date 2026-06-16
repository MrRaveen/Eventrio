package com.eventrio.notificationservice.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.listener.ChannelTopic;
import org.springframework.data.redis.listener.RedisMessageListenerContainer;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.function.Predicate;

@Slf4j
@Service
public class SseHubService {

    private static final long EMITTER_TIMEOUT_MS = Long.MAX_VALUE;

    private final RedisMessageListenerContainer listenerContainer;
    private final ObjectMapper objectMapper;
    private final ConcurrentHashMap<String, CopyOnWriteArrayList<FilteredEmitter>> emittersByChannel =
            new ConcurrentHashMap<>();
    private final Set<String> subscribedChannels = ConcurrentHashMap.newKeySet();

    public SseHubService(RedisMessageListenerContainer listenerContainer, ObjectMapper objectMapper) {
        this.listenerContainer = listenerContainer;
        this.objectMapper = objectMapper;
    }

    public SseEmitter subscribe(String channel) {
        return subscribe(channel, null);
    }

    public SseEmitter subscribe(String channel, Predicate<String> messageFilter) {
        SseEmitter emitter = new SseEmitter(EMITTER_TIMEOUT_MS);
        FilteredEmitter registration = new FilteredEmitter(emitter, messageFilter);
        emittersByChannel.computeIfAbsent(channel, key -> new CopyOnWriteArrayList<>()).add(registration);

        ensureChannelSubscribed(channel);

        Runnable cleanup = () -> removeEmitter(channel, registration);
        emitter.onCompletion(cleanup);
        emitter.onTimeout(cleanup);
        emitter.onError(ex -> cleanup.run());

        return emitter;
    }

    private void ensureChannelSubscribed(String channel) {
        if (subscribedChannels.add(channel)) {
            listenerContainer.addMessageListener((message, pattern) -> {
                String payload = new String(message.getBody());
                broadcast(channel, payload);
            }, new ChannelTopic(channel));
            log.info("Subscribed to Redis channel '{}'", channel);
        }
    }

    private void broadcast(String channel, String payload) {
        CopyOnWriteArrayList<FilteredEmitter> registrations = emittersByChannel.get(channel);
        if (registrations == null || registrations.isEmpty()) {
            return;
        }

        for (FilteredEmitter registration : registrations) {
            if (registration.filter() != null && !registration.filter().test(payload)) {
                continue;
            }
            try {
                registration.emitter().send(SseEmitter.event().data(payload));
            } catch (IOException ex) {
                log.debug("SSE send failed, removing emitter for channel {}", channel);
                removeEmitter(channel, registration);
            }
        }
    }

    private void removeEmitter(String channel, FilteredEmitter registration) {
        CopyOnWriteArrayList<FilteredEmitter> registrations = emittersByChannel.get(channel);
        if (registrations != null) {
            registrations.remove(registration);
            if (registrations.isEmpty()) {
                emittersByChannel.remove(channel, registrations);
            }
        }
        try {
            registration.emitter().complete();
        } catch (Exception ignored) {
            // emitter may already be completed
        }
    }

    public Predicate<String> userIdFilter(String userId) {
        return payload -> {
            try {
                Map<?, ?> parsed = objectMapper.readValue(payload, Map.class);
                Object payloadUserId = parsed.get("userID");
                return payloadUserId != null && userId.equals(payloadUserId.toString());
            } catch (Exception ex) {
                log.debug("Failed to parse notification payload for filtering: {}", ex.getMessage());
                return false;
            }
        };
    }

    private record FilteredEmitter(SseEmitter emitter, Predicate<String> filter) {
    }
}
