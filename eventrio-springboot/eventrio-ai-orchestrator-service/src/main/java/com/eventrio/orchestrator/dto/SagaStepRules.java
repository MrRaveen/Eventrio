package com.eventrio.orchestrator.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;

import java.util.ArrayList;
import java.util.List;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class SagaStepRules {

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class StepRule {
        private String name;
        private String function_name;
        private List<String> fallback_functions = new ArrayList<>();
    }

    private List<StepRule> main_steps = new ArrayList<>();
}
