package com.eventrio.common.enums;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum RolesEnum {
    ADMIN("Admin"),
    MANAGER("Manager"),
    WORKER("Worker");

    private final String value;

    RolesEnum(String value) {
        this.value = value;
    }

    @JsonValue
    public String getValue() {
        return value;
    }

    @JsonCreator
    public static RolesEnum fromValue(String value) {
        for (RolesEnum role : values()) {
            if (role.value.equals(value)) {
                return role;
            }
        }
        throw new IllegalArgumentException("Unknown RolesEnum value: " + value);
    }
}
