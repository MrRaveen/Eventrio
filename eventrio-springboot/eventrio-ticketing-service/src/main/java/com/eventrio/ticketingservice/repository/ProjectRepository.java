package com.eventrio.ticketingservice.repository;

import com.eventrio.ticketingservice.model.Project;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface ProjectRepository extends MongoRepository<Project, String> {
}
