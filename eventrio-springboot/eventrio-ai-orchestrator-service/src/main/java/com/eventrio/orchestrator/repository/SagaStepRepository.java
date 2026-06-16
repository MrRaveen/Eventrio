package com.eventrio.orchestrator.repository;

import com.eventrio.orchestrator.model.SagaStep;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface SagaStepRepository extends MongoRepository<SagaStep, String> {
}
