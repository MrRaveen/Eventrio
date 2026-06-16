package com.eventrio.ticketingservice.controller;

import com.eventrio.ticketingservice.dto.VerifyUserRequest;
import com.eventrio.ticketingservice.service.VerificationService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.Map;

@RestController
@RequestMapping("/customer")
@RequiredArgsConstructor
public class CustomerController {

    private final VerificationService verificationService;

    @GetMapping("/get-verification-code/{email}")
    public ResponseEntity<Map<String, Object>> getVerificationCode(@PathVariable String email) {
        Map<String, Object> result = verificationService.generateAndSendCode(email);
        return ResponseEntity.ok(result);
    }

    @PostMapping("/verify-user")
    public ResponseEntity<Map<String, String>> verifyUser(@Valid @RequestBody VerifyUserRequest request) {
        verificationService.verifyUserAndReserve(request);
        return ResponseEntity.ok(Map.of("message", "Successfully verified and reserved ticket"));
    }
}

@RestControllerAdvice
class CustomerExceptionHandler {

    @ExceptionHandler(VerificationService.VerificationException.class)
    public ResponseEntity<Map<String, String>> handleVerification(VerificationService.VerificationException ex) {
        return ResponseEntity.status(ex.getStatus()).body(Map.of("message", ex.getMessage()));
    }

    @ExceptionHandler(VerificationService.EmailSendException.class)
    public ResponseEntity<Map<String, String>> handleEmailSend(VerificationService.EmailSendException ex) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
                "message", ex.getMessage(),
                "error", ex.getErrorDetail() != null ? ex.getErrorDetail() : ""
        ));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, String>> handleGeneric(Exception ex) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
                "status", "error",
                "message", "An internal error occurred",
                "error", ex.getMessage() != null ? ex.getMessage() : "unknown"
        ));
    }
}
