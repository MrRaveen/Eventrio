package com.eventrio.orchestrator.repository;

import com.eventrio.orchestrator.model.SagaWorkflow;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface SagaWorkflowRepository extends MongoRepository<SagaWorkflow, String> {
}
