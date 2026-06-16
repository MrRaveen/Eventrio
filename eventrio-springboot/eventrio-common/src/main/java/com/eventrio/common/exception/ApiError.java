package com.eventrio.common.exception;

import lombok.Getter;

@Getter
public class ApiError extends RuntimeException {

    private final String errorCode;

    public ApiError(String errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }
}
