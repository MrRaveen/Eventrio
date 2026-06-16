package com.eventrio.orchestrator.service;

import com.eventrio.common.enums.SagaStepStatusEnum;
import com.eventrio.orchestrator.model.Project;
import com.eventrio.orchestrator.repository.ProjectRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class SagaStepExecutor {

    private final ProjectRepository projectRepository;
    private final SagaRedisCacheService cacheService;
    private final SagaChannelPublisher channelPublisher;

    @Async("sagaTaskExecutor")
    public void createGoogleDocForEvent(String userId, String workflowId) {
        runStubStep("create_google_doc_for_event", userId, workflowId, project -> {
            project.setScriptLink("https://docs.google.com/document/d/mock-" + project.getId() + "/edit");
        }, Map.of(
                "link", "https://docs.google.com/document/d/mock/edit",
                "message", "Successfully created your Google Doc (stub)"
        ));
    }

    @Async("sagaTaskExecutor")
    public void automateGoogleMeet(String userId, String workflowId) {
        runStubStep("automate_google_meet", userId, workflowId, project -> {
            project.setMeetingUrl("https://meet.google.com/mock-" + project.getId());
        }, Map.of("link", "https://meet.google.com/mock-link"));
    }

    @Async("sagaTaskExecutor")
    public void postImageToFacebookPage(String userId, String workflowId) {
        runStubStep("post_image_to_facebook_page", userId, workflowId, project -> {
            if (project.getFb_post() == null || project.getFb_post().isBlank()) {
                project.setFb_post("Check out our upcoming event: " + project.getName());
            }
        }, Map.of("message", "Successfully posted to Facebook page (stub)"));
    }

    @Async("sagaTaskExecutor")
    public void scheduleRealGoogleCalendar(String userId, String workflowId) {
        runStubStep("schedule_real_google_calendar", userId, workflowId, project -> {
            // Calendar step does not mutate project in Python; keep stub minimal.
        }, Map.of(
                "link", "https://calendar.google.com/event?mock=true",
                "message", "Successfully scheduled Event in your calendar (stub)"
        ));
    }

    private void runStubStep(
            String functionName,
            String userId,
            String workflowId,
            java.util.function.Consumer<Project> projectUpdater,
            Map<String, Object> successPayload) {

        long start = System.currentTimeMillis();
        try {
            Map<String, Object> cache = cacheService.readCache(userId, workflowId);
            String projectId = cache.get("projectID") != null ? cache.get("projectID").toString() : null;

            if (projectId != null) {
                projectRepository.findById(projectId).ifPresent(project -> {
                    projectUpdater.accept(project);
                    projectRepository.save(project);
                });
            }

            channelPublisher.publishStepCompletion(
                    functionName,
                    SagaStepStatusEnum.COMPLETED,
                    System.currentTimeMillis() - start,
                    userId,
                    workflowId,
                    projectId,
                    new HashMap<>(successPayload)
            );
        } catch (Exception ex) {
            log.error("{} failed for workflow {}: {}", functionName, workflowId, ex.getMessage(), ex);
            channelPublisher.publishStepCompletion(
                    functionName,
                    SagaStepStatusEnum.FAILED,
                    System.currentTimeMillis() - start,
                    userId,
                    workflowId,
                    cacheService.getProjectId(userId, workflowId),
                    Map.of("error", ex.getMessage())
            );
        }
    }
}
