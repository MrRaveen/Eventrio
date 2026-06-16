package com.eventrio.orchestrator.repository;

import com.eventrio.orchestrator.model.Project;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface ProjectRepository extends MongoRepository<Project, String> {
}
