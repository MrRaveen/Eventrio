package com.eventrio.common.exception;

import lombok.Getter;

/**
 * Placeholder for Flask's flask_limiter.errors.RateLimitExceeded.
 */
@Getter
public class RateLimitExceededException extends RuntimeException {

    public RateLimitExceededException(String message) {
        super(message);
    }

    public RateLimitExceededException(String message, Throwable cause) {
        super(message, cause);
    }
}
