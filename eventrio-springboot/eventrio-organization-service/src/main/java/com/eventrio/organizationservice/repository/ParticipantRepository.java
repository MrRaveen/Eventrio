package com.eventrio.organizationservice.repository;

import com.eventrio.organizationservice.model.Participant;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface ParticipantRepository extends MongoRepository<Participant, String> {

    void deleteByOrgID(String orgID);
}
