package com.eventrio.common.exception;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.NoHandlerFoundException;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ApiError.class)
    public ResponseEntity<ErrorResponse> handleApiError(ApiError error) {
        ErrorResponse response = new ErrorResponse(error.getErrorCode(), error.getMessage());
        log.error("APIError: {}", error.getMessage());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    @ExceptionHandler(RateLimitExceededException.class)
    public ResponseEntity<ErrorResponse> handleRateLimitExceeded(RateLimitExceededException error) {
        ErrorResponse response = new ErrorResponse("RATE_LIMIT_EXCEEDED", error.getMessage());
        log.warn("RateLimitExceeded: {}", error.getMessage());
        return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(response);
    }

    @ExceptionHandler(NoHandlerFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(NoHandlerFoundException error) {
        ErrorResponse response = new ErrorResponse("NOT_FOUND", error.getMessage());
        log.error("NotFound: {}", error.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(response);
    }

    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    public ResponseEntity<ErrorResponse> handleMethodNotAllowed(HttpRequestMethodNotSupportedException error) {
        ErrorResponse response = new ErrorResponse("METHOD_NOT_ALLOWED", error.getMessage());
        log.error("MethodNotAllowed: {}", error.getMessage());
        return ResponseEntity.status(HttpStatus.METHOD_NOT_ALLOWED).body(response);
    }

    @ExceptionHandler({
            HttpMessageNotReadableException.class,
            MethodArgumentNotValidException.class,
            IllegalArgumentException.class
    })
    public ResponseEntity<ErrorResponse> handleBadRequest(Exception error) {
        String message = error.getMessage();
        if (error instanceof MethodArgumentNotValidException validationError) {
            message = validationError.getBindingResult().getFieldErrors().stream()
                    .findFirst()
                    .map(fieldError -> fieldError.getField() + ": " + fieldError.getDefaultMessage())
                    .orElse(validationError.getMessage());
        }
        ErrorResponse response = new ErrorResponse("BAD_REQUEST", message);
        log.error("BadRequest: {}", message);
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }
}
