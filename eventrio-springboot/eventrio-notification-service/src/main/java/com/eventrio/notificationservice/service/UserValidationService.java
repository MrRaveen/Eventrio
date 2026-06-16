package com.eventrio.notificationservice.service;

import com.eventrio.notificationservice.model.UserAccount;
import com.eventrio.notificationservice.repository.UserAccountRepository;
import lombok.RequiredArgsConstructor;
import org.bson.types.ObjectId;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
@RequiredArgsConstructor
public class UserValidationService {

    private final UserAccountRepository userAccountRepository;

    public Optional<UserAccount> resolveUser(String userId) {
        if (userId == null || userId.isBlank()) {
            return Optional.empty();
        }

        Optional<UserAccount> bySub = userAccountRepository.findBySub(userId);
        if (bySub.isPresent()) {
            return bySub;
        }

        if (ObjectId.isValid(userId)) {
            return userAccountRepository.findById(userId);
        }

        return Optional.empty();
    }
}
