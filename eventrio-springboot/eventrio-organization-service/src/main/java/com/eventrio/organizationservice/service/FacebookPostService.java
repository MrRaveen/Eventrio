package com.eventrio.organizationservice.service;

import com.eventrio.organizationservice.model.Post;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.client.RestTemplate;

import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class FacebookPostService {

    private static final String FB_GRAPH_VERSION = "v19.0";

    private final RestTemplate restTemplate;

    public void deletePosts(List<Post> posts, String fbToken) {
        if (!StringUtils.hasText(fbToken) || posts == null) {
            return;
        }

        for (Post post : posts) {
            if (!StringUtils.hasText(post.getPostID())) {
                continue;
            }
            try {
                String deleteUrl = String.format(
                        "https://graph.facebook.com/%s/%s?access_token=%s",
                        FB_GRAPH_VERSION,
                        post.getPostID(),
                        fbToken
                );
                restTemplate.delete(deleteUrl);
            } catch (Exception ex) {
                log.warn("Facebook post deletion failed for {}: {}", post.getPostID(), ex.getMessage());
            }
        }
    }
}
