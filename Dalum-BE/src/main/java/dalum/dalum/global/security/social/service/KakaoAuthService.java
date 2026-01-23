package dalum.dalum.global.security.social.service;

import dalum.dalum.global.security.social.dto.response.KakaoTokenResponse;
import dalum.dalum.global.security.social.dto.response.KakaoUserInfoResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;

@Slf4j
@Service
@RequiredArgsConstructor
public class KakaoAuthService {

    private final WebClient webClient;

    @Value("${kakao.client-id}")
    private String clientId;

    @Value("${kakao.redirect-uri}")
    private String defaultRedirectUri;

    private static final String KAKAO_TOKEN_URI = "https://kauth.kakao.com/oauth/token";
    private static final String KAKAO_USER_INFO_URI = "https://kapi.kakao.com/v2/user/me";

    /**
     * 1. 인가 코드를 받아 액세스 토큰을 요청
     */
    public String getAccessToken(String code, String redirectUri) {
        String finalRedirectUri = (redirectUri != null && !redirectUri.isEmpty())
                ? redirectUri
                : defaultRedirectUri;

        MultiValueMap<String, String> formData = new LinkedMultiValueMap<>();
        formData.add("grant_type", "authorization_code");
        formData.add("client_id", clientId);
        formData.add("redirect_uri", finalRedirectUri);
        formData.add("code", code);

        log.info("=== 카카오 토큰 요청 ===");
        log.info("client_id: {}", clientId);
        log.info("redirect_uri: {}", finalRedirectUri);
        log.info("code: {}", code.substring(0, Math.min(10, code.length())) + "...");

        try {
            KakaoTokenResponse response = webClient.post()
                    .uri(KAKAO_TOKEN_URI)
                    .contentType(MediaType.APPLICATION_FORM_URLENCODED)
                    .body(BodyInserters.fromFormData(formData))
                    .retrieve()
                    .onStatus(status -> status.is4xxClientError() || status.is5xxServerError(),
                            clientResponse -> clientResponse.bodyToMono(String.class)
                                    .map(errorBody -> {
                                        log.error("카카오 API 에러 응답: {}", errorBody);
                                        return new RuntimeException("카카오 API 에러: " + errorBody);
                                    }))
                    .bodyToMono(KakaoTokenResponse.class)
                    .block();

            if (response == null || response.accessToken() == null) {
                log.error("카카오 토큰 발급 실패");
                throw new RuntimeException("카카오 토큰을 받아오지 못했습니다.");
            }

            return response.accessToken();
        } catch (Exception e) {
            log.error("카카오 토큰 요청 중 예외 발생: ", e);
            throw e;
        }
    }

    /**
     * 2. 액세스 토큰으로 사용자 정보를 요청
     */
    public KakaoUserInfoResponse getUserInfo(String accessToken) {

        // WebClient 요청 (GET)
        // 헤더에 Authorization: Bearer {token} 추가
        KakaoUserInfoResponse response = webClient.get()
                .uri(KAKAO_USER_INFO_URI)
                .header("Authorization", "Bearer " + accessToken)
                .header("Content-type", "application/x-www-form-urlencoded;charset=utf-8")
                .retrieve()
                .bodyToMono(KakaoUserInfoResponse.class)
                .block(); // 결과가 올 때까지 대기

        if (response == null) {
            log.error("카카오 유저 정보 조회 실패");
            throw new RuntimeException("카카오 유저 정보를 받아오지 못했습니다.");
        }

        return response;
    }
}
