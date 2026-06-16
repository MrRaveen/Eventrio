package com.eventrio.eventservice.repository;

import com.eventrio.eventservice.model.Task;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface TaskRepository extends MongoRepository<Task, String> {

    List<Task> findByEventId(String eventId);
}
