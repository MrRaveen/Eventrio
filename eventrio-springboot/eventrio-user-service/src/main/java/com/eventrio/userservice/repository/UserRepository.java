package com.eventrio.userservice.repository;

import com.eventrio.userservice.model.UserAccount;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.Optional;

public interface UserRepository extends MongoRepository<UserAccount, String> {

    Optional<UserAccount> findBySub(String sub);
}
