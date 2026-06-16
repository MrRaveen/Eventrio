package com.eventrio.eventservice.repository;

import com.eventrio.eventservice.model.Agenda;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.Optional;

public interface AgendaRepository extends MongoRepository<Agenda, String> {

    Optional<Agenda> findByEventID(String eventId);
}
