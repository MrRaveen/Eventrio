package com.eventrio.userservice.model;

import com.eventrio.common.enums.PlanOptionsEnum;
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

    @Builder.Default
    private String tier = PlanOptionsEnum.FREE.getValue();

    @Builder.Default
    private Instant joinedDate = Instant.now();

    private Instant lastRenewedDate;
    private Instant nextReniewDate;
}
