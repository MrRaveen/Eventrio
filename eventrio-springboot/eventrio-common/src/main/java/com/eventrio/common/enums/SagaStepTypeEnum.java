package com.eventrio.common.enums;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum SagaStepTypeEnum {
    AI_TASKS("execute_workflow"),
    UPDATE_PROJECT("update_project"),
    CREATE_GOOGLE_DOC("create_google_doc_for_event"),
    CREATE_GOOGLE_MEET("automate_google_meet"),
    CREATE_FB_PAGE("post_image_to_facebook_page"),
    CREATE_GOOGLE_CALENDAR("schedule_real_google_calendar");

    private final String value;

    SagaStepTypeEnum(String value) {
        this.value = value;
    }

    @JsonValue
    public String getValue() {
        return value;
    }

    @JsonCreator
    public static SagaStepTypeEnum fromValue(String value) {
        for (SagaStepTypeEnum type : values()) {
            if (type.value.equals(value)) {
                return type;
            }
        }
        throw new IllegalArgumentException("Unknown SagaStepTypeEnum value: " + value);
    }
}
