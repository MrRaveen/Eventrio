package com.eventrio.common.enums;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum IndustryEnum {
    IT("IT"),
    HEALTH_CARE("Health care"),
    SPORTS("Sports"),
    BUSINESS_EVENTS("Business events"),
    CASUAL("Casual"),
    EDUCATION("Education (school)"),
    COMPETITIONS("Competitions");

    private final String value;

    IndustryEnum(String value) {
        this.value = value;
    }

    @JsonValue
    public String getValue() {
        return value;
    }

    @JsonCreator
    public static IndustryEnum fromValue(String value) {
        for (IndustryEnum industry : values()) {
            if (industry.value.equals(value)) {
                return industry;
            }
        }
        throw new IllegalArgumentException("Unknown IndustryEnum value: " + value);
    }
}
