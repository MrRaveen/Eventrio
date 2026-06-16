package com.eventrio.eventservice.repository;

import com.eventrio.eventservice.model.Organization;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface OrganizationRepository extends MongoRepository<Organization, String> {
}
