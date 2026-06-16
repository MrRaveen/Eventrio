package com.eventrio.organizationservice.repository;

import com.eventrio.organizationservice.model.Organization;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.Optional;

public interface OrganizationRepository extends MongoRepository<Organization, String> {

    Optional<Organization> findByIdAndCreatedBy(String id, String createdBy);
}
