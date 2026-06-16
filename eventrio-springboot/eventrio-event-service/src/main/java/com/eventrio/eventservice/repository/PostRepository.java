package com.eventrio.eventservice.repository;

import com.eventrio.eventservice.model.Post;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface PostRepository extends MongoRepository<Post, String> {

    List<Post> findByProjectID(String projectId);
}
