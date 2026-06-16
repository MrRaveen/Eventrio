package com.eventrio.orchestrator.service;

import com.eventrio.orchestrator.dto.SagaStepRules;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import lombok.Getter;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Slf4j
@Service
public class SagaRulesService {

    private final ObjectMapper objectMapper;

    @Getter
    private List<SagaStepRules.StepRule> mainSteps = new ArrayList<>();

    public SagaRulesService(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @PostConstruct
    public void loadRules() {
        try (InputStream in = new ClassPathResource("step_rules/rules_v1.json").getInputStream()) {
            SagaStepRules rules = objectMapper.readValue(in, SagaStepRules.class);
            this.mainSteps = rules.getMain_steps() != null ? rules.getMain_steps() : List.of();
            log.info("Loaded {} SAGA step rules from rules_v1.json", mainSteps.size());
        } catch (Exception ex) {
            log.error("Failed to load step rules: {}", ex.getMessage());
            this.mainSteps = List.of();
        }
    }

    public Optional<String> findNextStep(String currentFunctionName) {
        for (int i = 0; i < mainSteps.size(); i++) {
            if (currentFunctionName.equals(mainSteps.get(i).getFunction_name())) {
                if (i + 1 < mainSteps.size()) {
                    return Optional.of(mainSteps.get(i + 1).getFunction_name());
                }
                return Optional.empty();
            }
        }
        return Optional.empty();
    }
}
