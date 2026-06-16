package com.eventrio.userservice.controller;

import com.eventrio.userservice.service.FacebookOAuthService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.net.URI;

@RestController
@RequiredArgsConstructor
public class FacebookOAuthController {

    private final FacebookOAuthService facebookOAuthService;

    @GetMapping("/connect/meta")
    public ResponseEntity<Void> connectMeta(
            @RequestHeader(value = "X-User-Id", required = false) String userId,
            HttpSession session) {
        if (StringUtils.hasText(userId)) {
            facebookOAuthService.bindSessionUser(session, userId);
        } else if (session != null && session.getAttribute("user_id") == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }

        URI redirectUri = facebookOAuthService.buildAuthorizationRedirect(session);
        return ResponseEntity.status(HttpStatus.FOUND)
                .header(HttpHeaders.LOCATION, redirectUri.toString())
                .build();
    }

    @GetMapping("/callbacks/meta")
    public ResponseEntity<Void> metaCallback(
            @RequestParam(value = "code", required = false) String code,
            @RequestParam(value = "state", required = false) String state,
            HttpSession session) {
        URI redirectUri = facebookOAuthService.handleCallback(code, state, session);
        return ResponseEntity.status(HttpStatus.FOUND)
                .header(HttpHeaders.LOCATION, redirectUri.toString())
                .build();
    }
}
