package com.eventrio.web.repository;

import com.eventrio.web.model.Task;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface TaskRepository extends MongoRepository<Task, String> {
    List<Task> findByEventId(String eventId);
}
