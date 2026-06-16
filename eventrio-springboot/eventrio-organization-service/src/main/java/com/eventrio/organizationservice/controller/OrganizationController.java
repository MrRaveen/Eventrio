package com.eventrio.organizationservice.controller;

import com.eventrio.common.dto.ApiResponse;
import com.eventrio.common.dto.CreateOrgRequest;
import com.eventrio.common.dto.OrgProjectSummary;
import com.eventrio.organizationservice.service.OrganizationService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/main-dashboard")
@RequiredArgsConstructor
public class OrganizationController {

    private final OrganizationService organizationService;

    @PostMapping("/create-org")
    public ResponseEntity<ApiResponse<String>> createOrg(
            @RequestHeader(value = "X-User-Id", required = false) String userId,
            @Valid @RequestBody CreateOrgRequest request) {
        if (!StringUtils.hasText(userId)) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(ApiResponse.errorMessage("error", "User not logged in"));
        }

        organizationService.createOrganization(userId, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Success", "Organization is created successfully"));
    }

    @PutMapping("/update-org/{orgId}")
    public ResponseEntity<ApiResponse<String>> updateOrg(
            @RequestHeader(value = "X-User-Id", required = false) String userId,
            @PathVariable String orgId,
            @Valid @RequestBody CreateOrgRequest request) {
        if (!StringUtils.hasText(userId)) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(ApiResponse.errorMessage("error", "User not logged in"));
        }

        organizationService.updateOrganization(userId, orgId, request);
        return ResponseEntity.ok(ApiResponse.success("Success", "Organization is updated successfully"));
    }

    @DeleteMapping("/remove-org/{orgId}")
    public ResponseEntity<ApiResponse<String>> removeOrg(
            @RequestHeader(value = "X-User-Id", required = false) String userId,
            @PathVariable String orgId) {
        if (!StringUtils.hasText(userId)) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(ApiResponse.errorMessage("error", "User not logged in."));
        }

        organizationService.removeOrganization(userId, orgId);
        return ResponseEntity.ok(ApiResponse.success("success",
                "Organization and all related data removed successfully."));
    }

    @GetMapping("/get-org-projects/{orgId}")
    public ResponseEntity<?> getOrgProjects(@PathVariable String orgId) {
        try {
            List<OrgProjectSummary> projects = organizationService.getOrgProjects(orgId);
            return ResponseEntity.ok(projects);
        } catch (Exception ex) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", ex.getMessage()));
        }
    }
}
