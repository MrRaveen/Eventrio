package com.eventrio.web.config;

import com.eventrio.web.service.UserAuthService;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@Component
@RequiredArgsConstructor
public class OAuth2SuccessHandler extends SimpleUrlAuthenticationSuccessHandler {

    private final UserAuthService userAuthService;

    @Override
    public void onAuthenticationSuccess(
            HttpServletRequest request,
            HttpServletResponse response,
            Authentication authentication) throws IOException, ServletException {

        OAuth2User oauthUser = (OAuth2User) authentication.getPrincipal();
        String sub = oauthUser.getAttribute("sub");
        String email = oauthUser.getAttribute("email");

        HttpSession session = request.getSession(true);
        session.setAttribute("user_id", sub);
        session.setAttribute("user_email", email);

        Map<String, Object> tokenMap = new HashMap<>(oauthUser.getAttributes());
        boolean existedBefore = userAuthService.isExistingUser(sub);
        userAuthService.upsertFromOAuth(oauthUser, tokenMap);

        if (existedBefore) {
            setDefaultTargetUrl("/dashboard");
        } else {
            setDefaultTargetUrl("/pricing");
        }
        setAlwaysUseDefaultTargetUrl(true);
        super.onAuthenticationSuccess(request, response, authentication);
    }
}
