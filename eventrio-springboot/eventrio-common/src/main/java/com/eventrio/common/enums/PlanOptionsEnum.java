package com.eventrio.common.enums;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum PlanOptionsEnum {
    FREE("free"),
    PRO("pro"),
    ULTIMATE("ultimate");

    private final String value;

    PlanOptionsEnum(String value) {
        this.value = value;
    }

    @JsonValue
    public String getValue() {
        return value;
    }

    @JsonCreator
    public static PlanOptionsEnum fromValue(String value) {
        for (PlanOptionsEnum plan : values()) {
            if (plan.value.equals(value)) {
                return plan;
            }
        }
        throw new IllegalArgumentException("Unknown PlanOptionsEnum value: " + value);
    }
}
