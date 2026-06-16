package com.eventrio.collaborationservice.repository;

import com.eventrio.collaborationservice.model.Contributor;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;
import java.util.Optional;

public interface ContributorRepository extends MongoRepository<Contributor, String> {

    List<Contributor> findByEventID(String eventId);

    List<Contributor> findByTargetEmail(String targetEmail);

    boolean existsByTargetEmailAndEventID(String targetEmail, String eventId);

    Optional<Contributor> findByEventIDAndUserAccountIDAndAcceptStatTrue(String eventId, String userAccountId);
}
