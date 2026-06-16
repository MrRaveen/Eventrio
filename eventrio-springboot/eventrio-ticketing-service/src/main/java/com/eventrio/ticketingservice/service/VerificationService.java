package com.eventrio.ticketingservice.service;

import com.eventrio.ticketingservice.dto.VerifyUserRequest;
import com.eventrio.ticketingservice.model.Participant;
import com.eventrio.ticketingservice.model.Project;
import com.eventrio.ticketingservice.repository.ParticipantRepository;
import com.eventrio.ticketingservice.repository.ProjectRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.mongodb.core.FindAndModifyOptions;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.data.mongodb.core.query.Update;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;

import java.security.SecureRandom;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Service
@RequiredArgsConstructor
public class VerificationService {

    private static final String REDIS_KEY_PREFIX = "verify_email:";
    private static final long CODE_TTL_SECONDS = 900L;
    private static final DateTimeFormatter EVENT_DATE_FORMAT =
            DateTimeFormatter.ofPattern("MMMM d, yyyy").withZone(ZoneOffset.UTC);

    private final StringRedisTemplate redisTemplate;
    private final ResendEmailService resendEmailService;
    private final ParticipantRepository participantRepository;
    private final ProjectRepository projectRepository;
    private final MongoTemplate mongoTemplate;
    private final SecureRandom secureRandom = new SecureRandom();

    public Map<String, Object> generateAndSendCode(String email) {
        String code = String.format("%06d", secureRandom.nextInt(1_000_000));
        String redisKey = REDIS_KEY_PREFIX + email;

        Boolean stored = redisTemplate.opsForValue().setIfAbsent(redisKey, code, CODE_TTL_SECONDS, TimeUnit.SECONDS);
        if (stored == null || !stored) {
            redisTemplate.opsForValue().set(redisKey, code, CODE_TTL_SECONDS, TimeUnit.SECONDS);
        }

        try {
            Map<String, Object> resendResponse = resendEmailService.sendVerificationCode(email, code);
            return Map.of(
                    "message", "Verification code sent successfully",
                    "data", resendResponse
            );
        } catch (RestClientException ex) {
            throw new EmailSendException(
                    "Failed to send email. Please check your Resend configuration.",
                    ex.getMessage()
            );
        }
    }

    public void verifyUserAndReserve(VerifyUserRequest request) {
        String redisKey = REDIS_KEY_PREFIX + request.getEmail();
        String storedCode = redisTemplate.opsForValue().get(redisKey);

        if (storedCode == null) {
            throw new VerificationException("Verification code expired or not found");
        }
        if (!storedCode.equals(request.getVerificationCode())) {
            throw new VerificationException("Invalid verification code");
        }

        Project project = projectRepository.findById(request.getEventID())
                .orElseThrow(() -> new VerificationException("Event not found", 404));

        if (participantRepository.findByEmailAndEventId(request.getEmail(), request.getEventID()).isPresent()) {
            throw new VerificationException("You have already reserved a ticket for this event.");
        }

        Participant participant = Participant.builder()
                .name(request.getName())
                .email(request.getEmail())
                .eventId(request.getEventID())
                .orgId(request.getOrgID())
                .verified(true)
                .createdDate(Instant.now())
                .build();
        participantRepository.save(participant);

        decrementAttendeeCount(request.getEventID());
        redisTemplate.delete(redisKey);

        String eventDate = project.getStartDate() != null
                ? EVENT_DATE_FORMAT.format(project.getStartDate())
                : "TBD";
        resendEmailService.sendConfirmationEmail(
                request.getEmail(),
                request.getName(),
                project.getName(),
                eventDate
        );
    }

    private void decrementAttendeeCount(String eventId) {
        Query query = Query.query(Criteria.where("_id").is(eventId));
        Update update = new Update().inc("attendeeCountExpected", -1);
        mongoTemplate.findAndModify(
                query,
                update,
                FindAndModifyOptions.options().returnNew(true),
                Project.class
        );
    }

    public static class VerificationException extends RuntimeException {
        private final int status;

        public VerificationException(String message) {
            this(message, 400);
        }

        public VerificationException(String message, int status) {
            super(message);
            this.status = status;
        }

        public int getStatus() {
            return status;
        }
    }

    public static class EmailSendException extends RuntimeException {
        private final String errorDetail;

        public EmailSendException(String message, String errorDetail) {
            super(message);
            this.errorDetail = errorDetail;
        }

        public String getErrorDetail() {
            return errorDetail;
        }
    }
}
