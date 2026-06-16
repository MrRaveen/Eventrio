package com.eventrio.collaborationservice.repository;

import com.eventrio.collaborationservice.model.Organization;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface OrganizationRepository extends MongoRepository<Organization, String> {
}
