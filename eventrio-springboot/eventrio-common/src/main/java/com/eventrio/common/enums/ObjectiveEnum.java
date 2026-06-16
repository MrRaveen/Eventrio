package com.eventrio.common.enums;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum ObjectiveEnum {
    LEAD_GENERATION("Lead generation"),
    INTERNAL_TRAINING("internal training"),
    NETWORKING("networking");

    private final String value;

    ObjectiveEnum(String value) {
        this.value = value;
    }

    @JsonValue
    public String getValue() {
        return value;
    }

    @JsonCreator
    public static ObjectiveEnum fromValue(String value) {
        for (ObjectiveEnum objective : values()) {
            if (objective.value.equals(value)) {
                return objective;
            }
        }
        throw new IllegalArgumentException("Unknown ObjectiveEnum value: " + value);
    }
}
