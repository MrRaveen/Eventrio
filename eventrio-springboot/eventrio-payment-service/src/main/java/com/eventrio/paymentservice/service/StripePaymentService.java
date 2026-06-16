package com.eventrio.paymentservice.service;

import com.eventrio.paymentservice.model.PaymentInfo;
import com.eventrio.paymentservice.model.UserAccount;
import com.eventrio.paymentservice.repository.UserAccountRepository;
import com.stripe.exception.SignatureVerificationException;
import com.stripe.exception.StripeException;
import com.stripe.model.Event;
import com.stripe.model.checkout.Session;
import com.stripe.net.Webhook;
import com.stripe.param.checkout.SessionCreateParams;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class StripePaymentService {

    private final UserAccountRepository userAccountRepository;

    @Value("${app.home-url:http://localhost:8080}")
    private String appHomeUrl;

    @Value("${stripe.webhook-secret:}")
    private String webhookSecret;

    public String createCheckoutSession(String userId, String planName, long planAmountCents) throws StripeException {
        SessionCreateParams params = SessionCreateParams.builder()
                .setMode(SessionCreateParams.Mode.PAYMENT)
                .addPaymentMethodType(SessionCreateParams.PaymentMethodType.CARD)
                .addLineItem(
                        SessionCreateParams.LineItem.builder()
                                .setQuantity(1L)
                                .setPriceData(
                                        SessionCreateParams.LineItem.PriceData.builder()
                                                .setCurrency("usd")
                                                .setUnitAmount(planAmountCents)
                                                .setProductData(
                                                        SessionCreateParams.LineItem.PriceData.ProductData.builder()
                                                                .setName(planName)
                                                                .build()
                                                )
                                                .build()
                                )
                                .build()
                )
                .setSuccessUrl(appHomeUrl + "/profile")
                .setCancelUrl(appHomeUrl + "/pricing")
                .setClientReferenceId(userId)
                .putMetadata("user_sub", userId)
                .putMetadata("planName", planName)
                .build();

        Session session = Session.create(params);
        return session.getUrl();
    }

    public void handleWebhook(String payload, String sigHeader) throws SignatureVerificationException {
        Event event = Webhook.constructEvent(payload, sigHeader, webhookSecret);

        if (!"checkout.session.completed".equals(event.getType())) {
            return;
        }

        Session session = (Session) event.getDataObjectDeserializer()
                .getObject()
                .orElse(null);

        if (session == null) {
            log.warn("Checkout session object missing from webhook event");
            return;
        }

        Map<String, String> metadata = session.getMetadata();
        if (metadata == null) {
            return;
        }

        String userSub = metadata.get("user_sub");
        String planName = metadata.getOrDefault("planName", "");

        if (userSub == null || userSub.isBlank()) {
            return;
        }

        userAccountRepository.findBySub(userSub).ifPresent(user -> {
            Instant now = Instant.now();
            String tier = resolveTier(planName);

            user.setAccStatus(List.of("Active"));
            user.setPayments(PaymentInfo.builder()
                    .tier(tier)
                    .lastRenewedDate(now)
                    .nextReniewDate(now.plus(30, ChronoUnit.DAYS))
                    .build());

            userAccountRepository.save(user);
            log.info("User {} activated successfully via webhook with tier: {}", userSub, tier);
        });
    }

    private String resolveTier(String planName) {
        if (planName == null || planName.isBlank()) {
            return "free";
        }
        String lower = planName.toLowerCase();
        if (lower.contains("ultimate")) {
            return "ultimate";
        }
        if (lower.contains("pro")) {
            return "pro";
        }
        return "free";
    }
}
