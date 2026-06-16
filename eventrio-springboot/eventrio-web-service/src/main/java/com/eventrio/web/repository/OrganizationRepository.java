package com.eventrio.web.repository;

import com.eventrio.web.model.Organization;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface OrganizationRepository extends MongoRepository<Organization, String> {
    List<Organization> findByCreatedBy(String createdBy);
}
