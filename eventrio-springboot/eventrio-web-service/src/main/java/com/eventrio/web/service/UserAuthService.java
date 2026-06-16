package com.eventrio.web.service;

import com.eventrio.common.dto.SetupProfileRequest;
import com.eventrio.common.enums.IndustryEnum;
import com.eventrio.common.enums.ObjectiveEnum;
import com.eventrio.common.enums.RoleEnum;
import com.eventrio.common.enums.ToolStackEnum;
import com.eventrio.web.model.UserAccount;
import com.eventrio.web.model.UserSpecificData;
import com.eventrio.web.repository.UserAccountRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class UserAuthService {

    private final UserAccountRepository userAccountRepository;

    public UserAccount findBySub(String sub) {
        return userAccountRepository.findBySub(sub).orElse(null);
    }

    public boolean isExistingUser(String sub) {
        return userAccountRepository.findBySub(sub).isPresent();
    }

    public UserAccount upsertFromOAuth(OAuth2User oauthUser, Map<String, Object> tokenAttributes) {
        String sub = oauthUser.getAttribute("sub");
        UserAccount existing = userAccountRepository.findBySub(sub).orElse(null);

        if (existing != null) {
            existing.setOauthToken(tokenAttributes != null ? new HashMap<>(tokenAttributes) : existing.getOauthToken());
            existing.setOnline(true);
            return userAccountRepository.save(existing);
        }

        UserAccount created = UserAccount.builder()
                .sub(sub)
                .email(oauthUser.getAttribute("email"))
                .emailVerified(Boolean.TRUE.equals(oauthUser.getAttribute("email_verified")))
                .displayName(oauthUser.getAttribute("name"))
                .givenName(oauthUser.getAttribute("given_name"))
                .familyName(oauthUser.getAttribute("family_name"))
                .profilePicUrl(oauthUser.getAttribute("picture"))
                .isOnline(true)
                .accStatus(new ArrayList<>(List.of("Pending-Payment")))
                .oauthToken(tokenAttributes != null ? new HashMap<>(tokenAttributes) : new HashMap<>())
                .build();
        return userAccountRepository.save(created);
    }

    public Map<String, Object> setupProfile(String userId, SetupProfileRequest request) {
        UserAccount user = userAccountRepository.findBySub(userId)
                .orElseThrow(() -> new IllegalStateException("User sequence not found in temporary storage."));

        UserSpecificData data = UserSpecificData.builder()
                .industry(enumValues(request.getIndustry()))
                .role(enumValues(request.getRole()))
                .averageAttendeeCount(request.getAverageAttendeeCount())
                .averageEventCountExcepected(request.getAverageEventCountExcepected())
                .toolStack(enumValues(request.getToolStack()))
                .mainObjectiveOfUser(enumValues(request.getMainObjectiveOfUser()))
                .build();

        user.setUserSpecificData(data);
        userAccountRepository.save(user);

        return Map.of(
                "status", "success",
                "redirect", "/dashboard"
        );
    }

    private <E extends Enum<E>> List<String> enumValues(List<E> values) {
        if (values == null) {
            return new ArrayList<>();
        }
        return values.stream()
                .map(v -> {
                    try {
                        var method = v.getClass().getMethod("getValue");
                        return (String) method.invoke(v);
                    } catch (Exception ignored) {
                        return v.name();
                    }
                })
                .collect(Collectors.toList());
    }

    public List<String> industryOptions() {
        return enumValues(List.of(IndustryEnum.values()));
    }

    public List<String> roleOptions() {
        return enumValues(List.of(RoleEnum.values()));
    }

    public List<String> objectiveOptions() {
        return enumValues(List.of(ObjectiveEnum.values()));
    }

    public List<String> toolOptions() {
        return enumValues(List.of(ToolStackEnum.values()));
    }
}
