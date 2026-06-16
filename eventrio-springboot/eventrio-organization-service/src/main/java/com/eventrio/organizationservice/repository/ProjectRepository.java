package com.eventrio.organizationservice.repository;

import com.eventrio.organizationservice.model.Project;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface ProjectRepository extends MongoRepository<Project, String> {

    List<Project> findByOrgID(String orgID);

    void deleteByOrgID(String orgID);
}
