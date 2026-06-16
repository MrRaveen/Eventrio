package com.eventrio.organizationservice.service;

import com.eventrio.organizationservice.config.AppConfig.CloudinaryProperties;
import com.eventrio.organizationservice.model.Project;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.util.StringUtils;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;

import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class CloudinaryService {

    private static final String CLOUDINARY_API_BASE = "https://api.cloudinary.com/v1_1";

    private final WebClient webClient;
    private final CloudinaryProperties cloudinaryProperties;

    public void cleanupProjectMedia(Project project) {
        if (project.getMediaLinks() != null) {
            for (String imageUrl : project.getMediaLinks()) {
                destroyFromUrl(imageUrl, "image");
            }
        }
        if (StringUtils.hasText(project.getSlideShowLink())) {
            destroyFromUrl(project.getSlideShowLink(), "raw");
        }
    }

    private void destroyFromUrl(String mediaUrl, String defaultResourceType) {
        if (!StringUtils.hasText(mediaUrl) || !StringUtils.hasText(cloudinaryProperties.cloudName())) {
            return;
        }

        String publicId = extractPublicId(mediaUrl);
        if (!StringUtils.hasText(publicId)) {
            return;
        }

        String resourceType = mediaUrl.endsWith(".pptx") ? "raw" : defaultResourceType;
        destroy(publicId, resourceType);
    }

    private void destroy(String publicId, String resourceType) {
        try {
            long timestamp = Instant.now().getEpochSecond();
            String signaturePayload = "public_id=" + publicId + "&timestamp=" + timestamp + cloudinaryProperties.apiSecret();
            String signature = sha1Hex(signaturePayload);

            MultiValueMap<String, String> form = new LinkedMultiValueMap<>();
            form.add("public_id", publicId);
            form.add("api_key", cloudinaryProperties.apiKey());
            form.add("timestamp", String.valueOf(timestamp));
            form.add("signature", signature);

            webClient.post()
                    .uri(CLOUDINARY_API_BASE + "/" + cloudinaryProperties.cloudName() + "/" + resourceType + "/destroy")
                    .contentType(MediaType.APPLICATION_FORM_URLENCODED)
                    .body(BodyInserters.fromFormData(form))
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
        } catch (Exception ex) {
            log.warn("Cloudinary deletion failed for {}: {}", publicId, ex.getMessage());
        }
    }

    static String extractPublicId(String mediaUrl) {
        try {
            URI uri = URI.create(mediaUrl);
            String path = uri.getPath();
            if (!StringUtils.hasText(path) || !path.contains("/upload/")) {
                return null;
            }

            String afterUpload = path.split("/upload/")[1];
            List<String> parts = new java.util.ArrayList<>(List.of(afterUpload.split("/")));
            if (!parts.isEmpty() && parts.get(0).startsWith("v") && parts.get(0).length() > 1
                    && parts.get(0).substring(1).chars().allMatch(Character::isDigit)) {
                parts.remove(0);
            }

            String publicIdWithExt = String.join("/", parts);
            int dotIndex = publicIdWithExt.lastIndexOf('.');
            if (dotIndex > 0) {
                return publicIdWithExt.substring(0, dotIndex);
            }
            return publicIdWithExt;
        } catch (Exception ex) {
            return null;
        }
    }

    private static String sha1Hex(String input) throws NoSuchAlgorithmException {
        MessageDigest digest = MessageDigest.getInstance("SHA-1");
        byte[] hash = digest.digest(input.getBytes(StandardCharsets.UTF_8));
        return HexFormat.of().formatHex(hash);
    }
}
