package com.eventrio.collaborationservice.controller;

import com.eventrio.collaborationservice.service.CollabDashboardService;
import com.eventrio.collaborationservice.service.ConflictException;
import com.eventrio.common.dto.ApiResponse;
import com.eventrio.common.dto.CollabDashboardDto;
import com.eventrio.common.exception.ResourceNotFoundException;
import com.eventrio.common.exception.ValidationException;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/main-dashboard")
@RequiredArgsConstructor
public class MainDashboardCollabController {

    private final CollabDashboardService collabDashboardService;

    @GetMapping("/get-collabs")
    public ResponseEntity<?> getCollabs(
            @RequestHeader(value = "X-User-Email", required = false) String userEmail) {
        if (userEmail == null || userEmail.isBlank()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(ApiResponse.fail("Unauthorized", "User email not found in session."));
        }

        try {
            List<CollabDashboardDto> collabs = collabDashboardService.getCollabs(userEmail);
            return ResponseEntity.ok(ApiResponse.success("Success", collabs));
        } catch (ValidationException ex) {
            return ResponseEntity.badRequest().body(ApiResponse.fail("Validation Error", ex.getMessage()));
        }
    }

    @PutMapping("/accept-collab/{docID}")
    public ResponseEntity<ApiResponse<String>> acceptCollab(
            @PathVariable String docID,
            @RequestHeader(value = "X-User-Id", required = false) String userId) {
        try {
            collabDashboardService.acceptCollab(docID, userId);
            return ResponseEntity.ok(ApiResponse.success("Success", "Collaboration accepted successfully."));
        } catch (ValidationException ex) {
            return ResponseEntity.badRequest().body(ApiResponse.fail("Validation Error", ex.getMessage()));
        } catch (ResourceNotFoundException ex) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(ApiResponse.fail("Not Found", ex.getMessage()));
        } catch (ConflictException ex) {
            return ResponseEntity.status(HttpStatus.CONFLICT)
                    .body(ApiResponse.fail("Conflict", ex.getMessage()));
        }
    }
}
