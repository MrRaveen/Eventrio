package com.eventrio.eventservice.repository;

import com.eventrio.eventservice.model.Project;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.time.Instant;
import java.util.List;

public interface ProjectRepository extends MongoRepository<Project, String> {

    List<Project> findByOwnerID(String ownerId);

    List<Project> findByStartDateAfterAndEndDateAfterOrderByStartDateAsc(Instant startDate, Instant endDate);
}
