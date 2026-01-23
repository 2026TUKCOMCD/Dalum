package dalum.dalum.global.security.social.service;

import dalum.dalum.global.security.social.dto.response.GoogleTokenResponse;
import dalum.dalum.global.security.social.dto.response.GoogleUserInfoResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;

import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;

@Service
@RequiredArgsConstructor
public class GoogleAuthService {

    private final WebClient webClient;

    @Value("${google.client-id}")
    private String clientId;

    @Value("${google.client-secret}")
    private String clientSecret;

    @Value("${google.redirect-uri}")
    private String defaultRedirectUri;

    @Value("${google.token-uri}")
    private String tokenUri;

    @Value("${google.user-info-uri}")
    private String userInfoUri;

    // 1. 액세스 토큰 발급
    public String getAccessToken(String code, String redirectUri) {

        // 프론트에서 받은 코드가 URL 인코딩 되어 있을 수 있으므로 디코딩 (선택 사항)
        String decodedCode = URLDecoder.decode(code, StandardCharsets.UTF_8);

        String finalRedirectUri = (redirectUri != null && !redirectUri.isEmpty())
                ? redirectUri
                : defaultRedirectUri;

        MultiValueMap<String, String> formData = new LinkedMultiValueMap<>();
        formData.add("code", decodedCode);
        formData.add("client_id", clientId);
        formData.add("client_secret", clientSecret); // 구글은 secret 필수적
        formData.add("redirect_uri", finalRedirectUri);
        formData.add("grant_type", "authorization_code");

        GoogleTokenResponse response = webClient.post()
                .uri(tokenUri)
                .contentType(MediaType.APPLICATION_FORM_URLENCODED)
                .body(BodyInserters.fromFormData(formData))
                .retrieve()
                .bodyToMono(GoogleTokenResponse.class)
                .block();

        if (response == null) {
            throw new RuntimeException("구글 토큰 발급 실패");
        }

        return response.accessToken();
    }

    // 2. 유저 정보 조회
    public GoogleUserInfoResponse getUserInfo(String accessToken) {
        GoogleUserInfoResponse response = webClient.get()
                .uri(userInfoUri)
                .header("Authorization", "Bearer " + accessToken)
                .retrieve()
                .bodyToMono(GoogleUserInfoResponse.class)
                .block();

        if (response == null) {
            throw new RuntimeException("구글 유저 정보 조회 실패");
        }

        return response;
    }
}