package com.eventrio.common.enums;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum SagaStepStatusEnum {
    COMPLETED("completed"),
    PENDING("pending"),
    FAILED("failed"),
    ERROR("error"),
    PROGRESS("progress");

    private final String value;

    SagaStepStatusEnum(String value) {
        this.value = value;
    }

    @JsonValue
    public String getValue() {
        return value;
    }

    @JsonCreator
    public static SagaStepStatusEnum fromValue(String value) {
        for (SagaStepStatusEnum status : values()) {
            if (status.value.equals(value)) {
                return status;
            }
        }
        throw new IllegalArgumentException("Unknown SagaStepStatusEnum value: " + value);
    }
}
