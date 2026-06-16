package com.eventrio.userservice.controller;

import com.eventrio.common.dto.FacebookPageResponse;
import com.eventrio.common.dto.OrgCountDeltaRequest;
import com.eventrio.common.dto.SetupProfileRequest;
import com.eventrio.common.dto.SocialStatusResponse;
import com.eventrio.userservice.model.UserAccount;
import com.eventrio.userservice.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping("/{sub}")
    public ResponseEntity<UserAccount> getUser(@PathVariable String sub) {
        return ResponseEntity.ok(userService.getUserBySub(sub));
    }

    @PostMapping("/setup-profile")
    public ResponseEntity<Map<String, Object>> setupProfile(
            @RequestHeader(value = "X-User-Id", required = false) String userId,
            @Valid @RequestBody SetupProfileRequest request) {
        if (!StringUtils.hasText(userId)) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of(
                    "status", "error",
                    "message", "User not logged in"
            ));
        }
        return ResponseEntity.ok(userService.setupProfile(userId, request));
    }

    @GetMapping("/{sub}/social-status")
    public ResponseEntity<SocialStatusResponse> socialStatus(@PathVariable String sub) {
        return ResponseEntity.ok(userService.getSocialStatus(sub));
    }

    @GetMapping("/{sub}/fb-pages")
    public ResponseEntity<List<FacebookPageResponse>> getFacebookPages(@PathVariable String sub) {
        return ResponseEntity.ok(userService.getFacebookPages(sub));
    }

    @PatchMapping("/{sub}/limits/org-count")
    public ResponseEntity<Map<String, String>> updateOrgCount(
            @PathVariable String sub,
            @Valid @RequestBody OrgCountDeltaRequest request) {
        userService.updateOrgCount(sub, request.getDelta());
        return ResponseEntity.ok(Map.of("message", "Success"));
    }

    @GetMapping("/{sub}/facebook-token")
    public ResponseEntity<Map<String, String>> getFacebookToken(@PathVariable String sub) {
        String token = userService.getFacebookToken(sub);
        if (token == null) {
            return ResponseEntity.ok(Map.of("token", ""));
        }
        return ResponseEntity.ok(Map.of("token", token));
    }
}
