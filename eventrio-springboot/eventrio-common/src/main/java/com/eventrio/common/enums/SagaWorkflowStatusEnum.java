package com.eventrio.common.enums;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum SagaWorkflowStatusEnum {
    ENDED("ended"),
    PROCESSING("processing"),
    COMPLETED("completed");

    private final String value;

    SagaWorkflowStatusEnum(String value) {
        this.value = value;
    }

    @JsonValue
    public String getValue() {
        return value;
    }

    @JsonCreator
    public static SagaWorkflowStatusEnum fromValue(String value) {
        for (SagaWorkflowStatusEnum status : values()) {
            if (status.value.equals(value)) {
                return status;
            }
        }
        throw new IllegalArgumentException("Unknown SagaWorkflowStatusEnum value: " + value);
    }
}
