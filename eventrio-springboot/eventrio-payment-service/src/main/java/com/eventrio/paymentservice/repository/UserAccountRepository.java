package com.eventrio.paymentservice.repository;

import com.eventrio.paymentservice.model.UserAccount;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.Optional;

public interface UserAccountRepository extends MongoRepository<UserAccount, String> {

    Optional<UserAccount> findBySub(String sub);
}
