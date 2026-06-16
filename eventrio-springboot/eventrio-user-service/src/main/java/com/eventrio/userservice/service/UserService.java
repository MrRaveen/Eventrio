package com.eventrio.userservice.service;

import com.eventrio.common.dto.FacebookPageResponse;
import com.eventrio.common.dto.SetupProfileRequest;
import com.eventrio.common.dto.SocialStatusResponse;
import com.eventrio.common.enums.IndustryEnum;
import com.eventrio.common.enums.ObjectiveEnum;
import com.eventrio.common.enums.RoleEnum;
import com.eventrio.common.enums.ToolStackEnum;
import com.eventrio.userservice.exception.ResourceNotFoundException;
import com.eventrio.userservice.model.SocialMediaTokens;
import com.eventrio.userservice.model.UserAccount;
import com.eventrio.userservice.model.UserSpecificData;
import com.eventrio.userservice.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class UserService {

    private static final String FB_GRAPH_VERSION = "v19.0";

    private final UserRepository userRepository;
    private final RestTemplate restTemplate;

    public UserAccount getUserBySub(String sub) {
        return userRepository.findBySub(sub)
                .orElseThrow(() -> new ResourceNotFoundException("User not found"));
    }

    public Map<String, Object> setupProfile(String userId, SetupProfileRequest request) {
        UserAccount user = userRepository.findBySub(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User sequence not found in temporary storage."));

        UserSpecificData data = UserSpecificData.builder()
                .industry(toIndustryValues(request.getIndustry()))
                .role(toRoleValues(request.getRole()))
                .averageAttendeeCount(request.getAverageAttendeeCount())
                .averageEventCountExcepected(request.getAverageEventCountExcepected())
                .toolStack(toToolStackValues(request.getToolStack()))
                .mainObjectiveOfUser(toObjectiveValues(request.getMainObjectiveOfUser()))
                .build();

        user.setUserSpecificData(data);
        userRepository.save(user);

        return Map.of(
                "status", "success",
                "redirect", "/dashboard"
        );
    }

    public SocialStatusResponse getSocialStatus(String sub) {
        UserAccount user = userRepository.findBySub(sub).orElse(null);
        if (user == null) {
            return SocialStatusResponse.builder()
                    .facebook(false)
                    .linkedIn(false)
                    .youtube(false)
                    .pinterest(false)
                    .build();
        }
        SocialMediaTokens tokens = user.getSocialMediaTokens();
        if (tokens == null) {
            tokens = SocialMediaTokens.builder().build();
        }

        return SocialStatusResponse.builder()
                .facebook(hasToken(tokens.getFacebook()))
                .linkedIn(hasToken(tokens.getLinkedIn()))
                .youtube(hasToken(tokens.getYoutube()))
                .pinterest(hasToken(tokens.getPinterest()))
                .build();
    }

    public List<FacebookPageResponse> getFacebookPages(String sub) {
        UserAccount user;
        try {
            user = getUserBySub(sub);
        } catch (ResourceNotFoundException ex) {
            return List.of();
        }

        SocialMediaTokens tokens = user.getSocialMediaTokens();
        List<FacebookPageResponse> pages = new ArrayList<>();

        if (tokens == null || !hasToken(tokens.getFacebook())) {
            return pages;
        }

        try {
            String url = String.format(
                    "https://graph.facebook.com/%s/me/accounts?access_token=%s",
                    FB_GRAPH_VERSION,
                    tokens.getFacebook()
            );

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);
            if (response == null) {
                return pages;
            }

            @SuppressWarnings("unchecked")
            List<Map<String, Object>> data = (List<Map<String, Object>>) response.get("data");
            if (data == null) {
                return pages;
            }

            for (Map<String, Object> page : data) {
                pages.add(new FacebookPageResponse(
                        String.valueOf(page.get("id")),
                        String.valueOf(page.get("name"))
                ));
            }
        } catch (Exception ex) {
            return pages;
        }
        return pages;
    }

    public void updateOrgCount(String sub, int delta) {
        UserAccount user = getUserBySub(sub);
        if (user.getLimits() == null) {
            user.setLimits(com.eventrio.userservice.model.Limits.builder().build());
        }
        int newCount = Math.max(0, user.getLimits().getOrgCount() + delta);
        user.getLimits().setOrgCount(newCount);
        userRepository.save(user);
    }

    public void saveFacebookToken(String userId, String longLivedToken) {
        UserAccount user = getUserBySub(userId);
        if (user.getSocialMediaTokens() == null) {
            user.setSocialMediaTokens(SocialMediaTokens.builder().build());
        }
        user.getSocialMediaTokens().setFacebook(longLivedToken);
        userRepository.save(user);
    }

    public String getFacebookToken(String sub) {
        UserAccount user = userRepository.findBySub(sub).orElse(null);
        if (user == null || user.getSocialMediaTokens() == null) {
            return null;
        }
        String token = user.getSocialMediaTokens().getFacebook();
        return hasToken(token) ? token : null;
    }

    private boolean hasToken(String token) {
        return StringUtils.hasText(token);
    }

    private List<String> toIndustryValues(List<IndustryEnum> industries) {
        if (industries == null) {
            return new ArrayList<>();
        }
        return industries.stream().map(IndustryEnum::getValue).collect(Collectors.toList());
    }

    private List<String> toRoleValues(List<RoleEnum> roles) {
        if (roles == null) {
            return new ArrayList<>();
        }
        return roles.stream().map(RoleEnum::getValue).collect(Collectors.toList());
    }

    private List<String> toToolStackValues(List<ToolStackEnum> toolStack) {
        if (toolStack == null) {
            return new ArrayList<>();
        }
        return toolStack.stream().map(ToolStackEnum::getValue).collect(Collectors.toList());
    }

    private List<String> toObjectiveValues(List<ObjectiveEnum> objectives) {
        if (objectives == null) {
            return new ArrayList<>();
        }
        return objectives.stream().map(ObjectiveEnum::getValue).collect(Collectors.toList());
    }
}
