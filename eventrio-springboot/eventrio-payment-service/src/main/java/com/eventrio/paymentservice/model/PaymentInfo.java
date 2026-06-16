package com.eventrio.paymentservice.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PaymentInfo {

    private String tier;

    private Instant joinedDate;

    private Instant lastRenewedDate;

    private Instant nextReniewDate;
}
