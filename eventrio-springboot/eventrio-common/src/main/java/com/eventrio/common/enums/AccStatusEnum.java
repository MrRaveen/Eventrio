package com.eventrio.common.enums;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum AccStatusEnum {
    ACTIVE("Active"),
    D_ACTIVATED("D-activated"),
    PENDING_PAYMENT("Pending-Payment");

    private final String value;

    AccStatusEnum(String value) {
        this.value = value;
    }

    @JsonValue
    public String getValue() {
        return value;
    }

    @JsonCreator
    public static AccStatusEnum fromValue(String value) {
        for (AccStatusEnum status : values()) {
            if (status.value.equals(value)) {
                return status;
            }
        }
        throw new IllegalArgumentException("Unknown AccStatusEnum value: " + value);
    }
}
