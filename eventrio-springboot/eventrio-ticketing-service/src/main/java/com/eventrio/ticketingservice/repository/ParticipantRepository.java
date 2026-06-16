package com.eventrio.ticketingservice.repository;

import com.eventrio.ticketingservice.model.Participant;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.Optional;

public interface ParticipantRepository extends MongoRepository<Participant, String> {

    Optional<Participant> findByEmailAndEventId(String email, String eventId);
}
