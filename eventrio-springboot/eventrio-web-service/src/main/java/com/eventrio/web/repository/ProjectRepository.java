package com.eventrio.web.repository;

import com.eventrio.web.model.Project;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.time.Instant;
import java.util.List;

public interface ProjectRepository extends MongoRepository<Project, String> {
    List<Project> findByStartDateAfterAndEndDateAfterOrderByStartDateAsc(Instant startDate, Instant endDate);
}
