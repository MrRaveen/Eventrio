package com.eventrio.common.enums;

public enum CollaboratorRole {
    ADMIN("Admin"),
    MANAGER("Manager"),
    WORKER("Worker");

    private final String value;

    CollaboratorRole(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }

    public static CollaboratorRole fromValue(String value) {
        for (CollaboratorRole role : values()) {
            if (role.value.equals(value)) {
                return role;
            }
        }
        throw new IllegalArgumentException("Invalid role: " + value);
    }
}
