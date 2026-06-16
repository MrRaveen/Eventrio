package com.eventrio.organizationservice.repository;

import com.eventrio.organizationservice.model.Post;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface PostRepository extends MongoRepository<Post, String> {

    List<Post> findByOrgID(String orgID);

    void deleteByOrgID(String orgID);
}
