package com.eventrio.web.controller;

import com.eventrio.common.dto.SetupProfileRequest;
import com.eventrio.web.service.UserAuthService;
import jakarta.servlet.http.HttpSession;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.Map;

@Controller
@RequiredArgsConstructor
public class AuthController {

    private final UserAuthService userAuthService;

    @GetMapping("/login")
    public String login() {
        return "login";
    }

    @PostMapping("/setup-profile")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> setupProfile(
            HttpSession session,
            @Valid @RequestBody SetupProfileRequest request) {

        String userId = (String) session.getAttribute("user_id");
        if (userId == null || userId.isBlank()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of(
                    "status", "error",
                    "message", "User not logged in"
            ));
        }

        try {
            return ResponseEntity.ok(userAuthService.setupProfile(userId, request));
        } catch (IllegalStateException ex) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
                    "status", "error",
                    "message", ex.getMessage()
            ));
        } catch (Exception ex) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
                    "status", "error",
                    "message", "An unexpected error occurred: " + ex.getMessage()
            ));
        }
    }
}
