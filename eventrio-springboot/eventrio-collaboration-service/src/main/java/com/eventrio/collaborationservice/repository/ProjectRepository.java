package com.eventrio.collaborationservice.repository;

import com.eventrio.collaborationservice.model.Project;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface ProjectRepository extends MongoRepository<Project, String> {
}
