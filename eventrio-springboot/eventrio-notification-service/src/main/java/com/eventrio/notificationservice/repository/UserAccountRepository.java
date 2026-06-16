package com.eventrio.notificationservice.repository;

import com.eventrio.notificationservice.model.UserAccount;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.Optional;

public interface UserAccountRepository extends MongoRepository<UserAccount, String> {

    Optional<UserAccount> findBySub(String sub);
}
