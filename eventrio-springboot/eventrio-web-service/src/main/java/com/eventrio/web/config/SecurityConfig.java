package com.eventrio.web.config;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final OAuth2SuccessHandler oAuth2SuccessHandler;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .csrf(csrf -> csrf
                        .ignoringRequestMatchers(
                                "/setup-profile",
                                "/ai/**",
                                "/testing/**",
                                "/main-dashboard/**",
                                "/event-ui/**",
                                "/customer/**",
                                "/payment/**",
                                "/notifications/**"
                        ))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers(
                                "/",
                                "/pricing",
                                "/browse-events",
                                "/customer/**",
                                "/login",
                                "/login/**",
                                "/oauth2/**",
                                "/error",
                                "/css/**",
                                "/js/**",
                                "/images/**",
                                "/webjars/**"
                        ).permitAll()
                        .requestMatchers(
                                "/dashboard",
                                "/ai-planner",
                                "/user-profile-ui",
                                "/event-dashboard/**"
                        ).authenticated()
                        .anyRequest().permitAll()
                )
                .oauth2Login(oauth -> oauth
                        .loginPage("/login")
                        .successHandler(oAuth2SuccessHandler)
                )
                .logout(logout -> logout
                        .logoutUrl("/logout")
                        .logoutSuccessUrl("/")
                        .invalidateHttpSession(true)
                        .deleteCookies("EVENTRIO_SESSION", "JSESSIONID")
                );

        return http.build();
    }
}
