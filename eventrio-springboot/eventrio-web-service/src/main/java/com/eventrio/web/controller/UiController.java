package com.eventrio.web.controller;

import com.eventrio.common.dto.BrowseEventDto;
import com.eventrio.web.model.Project;
import com.eventrio.web.model.Task;
import com.eventrio.web.model.UserAccount;
import com.eventrio.web.service.UiDataService;
import com.eventrio.web.service.UserAuthService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.List;
import java.util.Map;

@Controller
@RequiredArgsConstructor
public class UiController {

    private final UserAuthService userAuthService;
    private final UiDataService uiDataService;

    @GetMapping("/")
    public String landing() {
        return "landing";
    }

    @GetMapping("/pricing")
    public String pricing() {
        return "pricing";
    }

    @GetMapping("/user-profile-ui")
    public String userProfileUi(Model model) {
        model.addAttribute("industries", userAuthService.industryOptions());
        model.addAttribute("roles", userAuthService.roleOptions());
        model.addAttribute("objectives", userAuthService.objectiveOptions());
        model.addAttribute("tools", userAuthService.toolOptions());
        return "profile_setup";
    }

    @GetMapping("/dashboard")
    public String dashboard(
            @RequestParam(value = "tab", defaultValue = "orgs") String tab,
            HttpSession session,
            Model model) {

        String userId = (String) session.getAttribute("user_id");
        UserAccount user = userId != null ? userAuthService.findBySub(userId) : null;
        List<Map<String, Object>> orgs = userId != null
                ? uiDataService.getOrganizationsForUser(userId)
                : List.of();

        model.addAttribute("active_tab", tab);
        model.addAttribute("orgs", orgs);
        model.addAttribute("user", user);
        model.addAttribute("industries", userAuthService.industryOptions());
        model.addAttribute("roles", userAuthService.roleOptions());
        return "dashboard";
    }

    @GetMapping("/ai-planner")
    public String aiPlanner(HttpSession session, Model model) {
        String userId = (String) session.getAttribute("user_id");
        UserAccount user = userId != null ? userAuthService.findBySub(userId) : null;
        List<Map<String, Object>> orgs = userId != null
                ? uiDataService.getOrganizationsForUser(userId)
                : List.of();

        model.addAttribute("active_tab", "ai-planner");
        model.addAttribute("user", user);
        model.addAttribute("orgs", orgs);
        return "ai_planner";
    }

    @GetMapping("/event-dashboard/{eventId}")
    public String eventDashboard(
            @PathVariable String eventId,
            @RequestParam(value = "tab", defaultValue = "tasks") String tab,
            Model model) {

        try {
            Project event = uiDataService.getEventOrThrow(eventId);
            String scriptText = uiDataService.extractScriptText(event);
            List<Task> eventTasks = uiDataService.getEventTasks(eventId);

            model.addAttribute("event", event);
            model.addAttribute("script_text", scriptText);
            model.addAttribute("active_tab", tab);
            model.addAttribute("event_tasks", eventTasks);
            return "event_dashboard";
        } catch (IllegalArgumentException ex) {
            model.addAttribute("error_code", "404");
            model.addAttribute("error_title", "Event Not Found");
            model.addAttribute("error_message", ex.getMessage());
            return "error";
        }
    }

    @GetMapping("/browse-events")
    public String browseEvents(
            @RequestParam(value = "selected", required = false) String selected,
            Model model) {

        List<BrowseEventDto> events = uiDataService.getBrowseEvents();
        BrowseEventDto selectedEvent = null;

        if (selected != null) {
            selectedEvent = events.stream()
                    .filter(e -> selected.equals(e.getId()))
                    .findFirst()
                    .orElse(null);
        }
        if (selectedEvent == null && !events.isEmpty()) {
            selectedEvent = events.get(0);
        }

        model.addAttribute("events", events);
        model.addAttribute("selected_event", selectedEvent);
        return "browse_events";
    }
}
