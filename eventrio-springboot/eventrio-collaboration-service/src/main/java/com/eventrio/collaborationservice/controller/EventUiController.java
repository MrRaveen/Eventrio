package com.eventrio.collaborationservice.controller;

import com.eventrio.collaborationservice.dto.AssignTaskRequest;
import com.eventrio.collaborationservice.dto.RoleUpdateRequest;
import com.eventrio.collaborationservice.dto.SendInvitationRequest;
import com.eventrio.collaborationservice.dto.UpdateTaskRequest;
import com.eventrio.collaborationservice.service.CollabDropdownService;
import com.eventrio.collaborationservice.service.ContributorService;
import com.eventrio.collaborationservice.service.MailjetDeliveryException;
import com.eventrio.collaborationservice.service.TaskService;
import com.eventrio.common.dto.ApiResponse;
import com.eventrio.common.dto.CollabDropdownDto;
import com.eventrio.common.dto.ContributorDto;
import com.eventrio.common.exception.ResourceNotFoundException;
import com.eventrio.common.exception.ValidationException;
import com.eventrio.collaborationservice.service.ConflictException;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/event-ui")
@RequiredArgsConstructor
public class EventUiController {

    private final ContributorService contributorService;
    private final CollabDropdownService collabDropdownService;
    private final TaskService taskService;

    @GetMapping("/get-roles")
    public ResponseEntity<ApiResponse<List<String>>> getRoles() {
        return ResponseEntity.ok(ApiResponse.success("Success", contributorService.getRoles()));
    }

    @PostMapping("/get-media/{eventID}")
    public ResponseEntity<?> getMedia(@PathVariable String eventID) {
        try {
            List<String> media = contributorService.getMedia(eventID);
            return ResponseEntity.ok(ApiResponse.success("success", media));
        } catch (ResourceNotFoundException ex) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(ApiResponse.fail("error", ex.getMessage()));
        } catch (Exception ex) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.fail("error", "An error occurred: " + ex.getMessage()));
        }
    }

    @GetMapping("/view-contributors/{eventID}")
    public ResponseEntity<?> viewContributors(@PathVariable String eventID) {
        try {
            List<ContributorDto> contributors = contributorService.viewContributors(eventID);
            return ResponseEntity.ok(ApiResponse.success("Success", contributors));
        } catch (ValidationException ex) {
            return ResponseEntity.badRequest().body(ApiResponse.fail("Validation Error", ex.getMessage()));
        }
    }

    @PutMapping("/update-contributor-role/{docID}")
    public ResponseEntity<ApiResponse<String>> updateContributorRole(
            @PathVariable String docID,
            @RequestBody RoleUpdateRequest request) {
        try {
            contributorService.updateContributorRole(docID, request != null ? request.getRoleName() : null);
            return ResponseEntity.ok(ApiResponse.success("Success", "Contributor role updated successfully."));
        } catch (ValidationException ex) {
            return ResponseEntity.badRequest().body(ApiResponse.fail("Validation Error", ex.getMessage()));
        } catch (ResourceNotFoundException ex) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(ApiResponse.fail("Not Found", ex.getMessage()));
        }
    }

    @PostMapping("/send-invitation")
    public ResponseEntity<ApiResponse<String>> sendInvitation(@RequestBody SendInvitationRequest request) {
        try {
            contributorService.sendInvitation(request);
            return ResponseEntity.ok(ApiResponse.success("Success", "Invitation sent successfully."));
        } catch (ValidationException ex) {
            return ResponseEntity.badRequest().body(ApiResponse.fail("Validation Error", ex.getMessage()));
        } catch (ResourceNotFoundException ex) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(ApiResponse.fail("Not Found", ex.getMessage()));
        } catch (ConflictException ex) {
            return ResponseEntity.status(HttpStatus.CONFLICT)
                    .body(ApiResponse.fail("Conflict", ex.getMessage()));
        } catch (MailjetDeliveryException ex) {
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                    .body(ApiResponse.fail("Email Delivery Failed", ex.getMessage()));
        }
    }

    @GetMapping("/get-collabs-dropdown/{eventID}")
    public ResponseEntity<?> getCollabsDropdown(@PathVariable String eventID) {
        try {
            List<CollabDropdownDto> collabs = collabDropdownService.getCollabsDropdown(eventID);
            return ResponseEntity.ok(ApiResponse.success("Success", collabs));
        } catch (ValidationException ex) {
            return ResponseEntity.badRequest().body(ApiResponse.fail("Validation Error", ex.getMessage()));
        }
    }

    @PutMapping("/assign-task/{docID}")
    public ResponseEntity<ApiResponse<String>> assignTask(
            @PathVariable String docID,
            @RequestBody AssignTaskRequest request) {
        try {
            taskService.assignTask(docID, request);
            return ResponseEntity.ok(ApiResponse.success("Success", "User assigned to task successfully."));
        } catch (ValidationException ex) {
            return ResponseEntity.badRequest().body(ApiResponse.fail("Validation Error", ex.getMessage()));
        } catch (ResourceNotFoundException ex) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(ApiResponse.fail("Not Found", ex.getMessage()));
        }
    }

    @PutMapping("/update-task/{docID}")
    public ResponseEntity<ApiResponse<String>> updateTask(
            @PathVariable String docID,
            @RequestBody UpdateTaskRequest request) {
        try {
            taskService.updateTask(docID, request);
            return ResponseEntity.ok(ApiResponse.success("Success", "Task details updated successfully."));
        } catch (ValidationException ex) {
            return ResponseEntity.badRequest().body(ApiResponse.fail("Validation Error", ex.getMessage()));
        } catch (ResourceNotFoundException ex) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(ApiResponse.fail("Not Found", ex.getMessage()));
        }
    }

    @DeleteMapping("/delete-task/{docID}")
    public ResponseEntity<ApiResponse<String>> deleteTask(@PathVariable String docID) {
        try {
            taskService.deleteTask(docID);
            return ResponseEntity.ok(ApiResponse.success("Success", "Task deleted successfully."));
        } catch (ValidationException ex) {
            return ResponseEntity.badRequest().body(ApiResponse.fail("Validation Error", ex.getMessage()));
        } catch (ResourceNotFoundException ex) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(ApiResponse.fail("Not Found", ex.getMessage()));
        }
    }

    @PutMapping("/unassign-task/{docID}")
    public ResponseEntity<ApiResponse<String>> unassignTask(@PathVariable String docID) {
        try {
            taskService.unassignTask(docID);
            return ResponseEntity.ok(ApiResponse.success("Success", "Task assignment removed successfully."));
        } catch (ValidationException ex) {
            return ResponseEntity.badRequest().body(ApiResponse.fail("Validation Error", ex.getMessage()));
        } catch (ResourceNotFoundException ex) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(ApiResponse.fail("Not Found", ex.getMessage()));
        }
    }

    @DeleteMapping("/remove-contributor/{docID}")
    public ResponseEntity<ApiResponse<String>> removeContributor(@PathVariable String docID) {
        try {
            contributorService.removeContributor(docID);
            return ResponseEntity.ok(ApiResponse.success("Success", "Contributor removed successfully."));
        } catch (ValidationException ex) {
            return ResponseEntity.badRequest().body(ApiResponse.fail("Validation Error", ex.getMessage()));
        } catch (ResourceNotFoundException ex) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(ApiResponse.fail("Not Found", ex.getMessage()));
        }
    }
}
