package com.eventrio.common.enums;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum RoleEnum {
    MANAGER("manager"),
    STUDENT("student"),
    BUSINESS_OWNER("business owner"),
    EVENT_PLANNER("event planner"),
    TEACHER("teacher"),
    SPORT_COACH("sport coach");

    private final String value;

    RoleEnum(String value) {
        this.value = value;
    }

    @JsonValue
    public String getValue() {
        return value;
    }

    @JsonCreator
    public static RoleEnum fromValue(String value) {
        for (RoleEnum role : values()) {
            if (role.value.equals(value)) {
                return role;
            }
        }
        throw new IllegalArgumentException("Unknown RoleEnum value: " + value);
    }
}
