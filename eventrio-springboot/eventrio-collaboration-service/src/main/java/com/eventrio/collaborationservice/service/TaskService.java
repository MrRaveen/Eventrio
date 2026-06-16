package com.eventrio.collaborationservice.service;

import com.eventrio.collaborationservice.dto.AssignTaskRequest;
import com.eventrio.collaborationservice.dto.UpdateTaskRequest;
import com.eventrio.collaborationservice.model.Task;
import com.eventrio.collaborationservice.repository.ContributorRepository;
import com.eventrio.collaborationservice.repository.TaskRepository;
import com.eventrio.common.enums.TaskPriority;
import com.eventrio.common.enums.TaskStatus;
import com.eventrio.common.exception.ResourceNotFoundException;
import com.eventrio.common.exception.ValidationException;
import lombok.RequiredArgsConstructor;
import org.bson.types.ObjectId;
import org.springframework.stereotype.Service;

import java.time.Instant;

@Service
@RequiredArgsConstructor
public class TaskService {

    private final TaskRepository taskRepository;
    private final ContributorRepository contributorRepository;

    public void assignTask(String docId, AssignTaskRequest request) {
        if (request == null || request.getUserID() == null) {
            throw new ValidationException("Missing 'userID' in JSON payload.");
        }

        String userId = request.getUserID();
        if (userId.isBlank()) {
            throw new ValidationException("'userID' cannot be empty.");
        }

        Task task = findTaskById(docId);

        boolean isMember = contributorRepository
                .findByEventIDAndUserAccountIDAndAcceptStatTrue(task.getEventId(), userId.strip())
                .isPresent();

        if (!isMember) {
            throw new ValidationException("Target user is not an accepted collaborator for this project.");
        }

        task.setAssigned_to(userId.strip());
        taskRepository.save(task);
    }

    public void updateTask(String docId, UpdateTaskRequest request) {
        if (request == null) {
            throw new ValidationException("Missing JSON payload.");
        }

        Task task = findTaskById(docId);

        if (request.getTitle() != null) {
            if (request.getTitle().isBlank()) {
                throw new ValidationException("Title is required and cannot be empty.");
            }
            task.setTitle(request.getTitle().strip());
        }

        if (request.getDescription() != null) {
            task.setDescription(request.getDescription());
        }

        if (request.getPriority() != null) {
            try {
                TaskPriority priority = TaskPriority.fromValue(request.getPriority());
                task.setPriority(priority.getValue());
            } catch (IllegalArgumentException ex) {
                throw new ValidationException(
                        "Invalid priority. Allowed values: lowest, low, medium, high, critical"
                );
            }
        }

        if (request.getStatus() != null) {
            try {
                TaskStatus status = TaskStatus.fromValue(request.getStatus());
                task.setStatus(status.getValue());
            } catch (IllegalArgumentException ex) {
                throw new ValidationException(
                        "Invalid status. Allowed values: in progress, done, under review, cancelled"
                );
            }
        }

        if (request.getStartDate() != null) {
            task.setStartDate(parseInstant(request.getStartDate(), "startDate"));
        }

        if (request.getDeadline() != null) {
            task.setDeadline(parseInstant(request.getDeadline(), "deadline"));
        }

        taskRepository.save(task);
    }

    public void deleteTask(String docId) {
        if (docId == null || docId.isBlank()) {
            throw new ValidationException("Document ID is required.");
        }

        Task task = findTaskById(docId.strip());
        taskRepository.delete(task);
    }

    public void unassignTask(String docId) {
        if (docId == null || docId.isBlank()) {
            throw new ValidationException("Document ID is required.");
        }

        Task task = findTaskById(docId.strip());
        task.setAssigned_to(null);
        taskRepository.save(task);
    }

    private Task findTaskById(String docId) {
        if (!ObjectId.isValid(docId)) {
            throw new ValidationException("Invalid Document ID format.");
        }

        return taskRepository.findById(docId.strip())
                .orElseThrow(() -> new ResourceNotFoundException("Task not found."));
    }

    private Instant parseInstant(String value, String fieldName) {
        if (value == null || value.isBlank()) {
            return null;
        }
        try {
            return Instant.parse(value.replace("Z", "+00:00"));
        } catch (Exception ex) {
            throw new ValidationException(
                    "Invalid " + fieldName + " format. Must be an ISO 8601 string."
            );
        }
    }
}
