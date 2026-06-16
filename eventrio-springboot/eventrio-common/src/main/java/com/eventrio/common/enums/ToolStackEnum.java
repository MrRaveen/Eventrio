package com.eventrio.common.enums;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum ToolStackEnum {
    GOOGLE_DOC("Google Doc"),
    GOOGLE_MEET("Google Meet"),
    GOOGLE_CALENDAR("Google Calendar");

    private final String value;

    ToolStackEnum(String value) {
        this.value = value;
    }

    @JsonValue
    public String getValue() {
        return value;
    }

    @JsonCreator
    public static ToolStackEnum fromValue(String value) {
        for (ToolStackEnum tool : values()) {
            if (tool.value.equals(value)) {
                return tool;
            }
        }
        throw new IllegalArgumentException("Unknown ToolStackEnum value: " + value);
    }
}
