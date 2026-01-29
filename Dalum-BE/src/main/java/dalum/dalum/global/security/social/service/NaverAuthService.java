package dalum.dalum.global.security.social.service;

import dalum.dalum.domain.auth.exception.AuthException;
import dalum.dalum.domain.auth.exception.code.AuthErrorCode;
import dalum.dalum.global.security.social.dto.response.NaverTokenResponse;
import dalum.dalum.global.security.social.dto.response.NaverUserInfoResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.web.reactive.function.client.WebClient;

import java.math.BigInteger;
import java.security.SecureRandom;

@Service
@RequiredArgsConstructor
public class NaverAuthService {

    private final WebClient webClient;

    @Value("${naver.client-id}")
    private String clientId;

    @Value("${naver.client-secret}")
    private String clientSecret;

    @Value("${naver.token-uri}")
    private String tokenUri;

    @Value("${naver.user-info-uri}")
    private String userInfoUri;

    public String getAccessToken(String code) {
        String state = new BigInteger(130, new SecureRandom()).toString(32);

        LinkedMultiValueMap<Object, Object> params = new LinkedMultiValueMap<>();
        params.add("grant_type", "authorization_code");
        params.add("client_id", clientId);
        params.add("client_secret", clientSecret);
        params.add("code", code);
        params.add("state", state);

        NaverTokenResponse response = webClient.post()
                .uri(tokenUri)
                .bodyValue(params)
                .retrieve()
                .bodyToMono(NaverTokenResponse.class)
                .block();

        if (response == null || response.accessToken() == null) {
            throw new AuthException(AuthErrorCode.INTERNAL_SERVER_ERROR);
        }

        return response.accessToken();
    }

    public NaverUserInfoResponse getUserInfo(String accessToken) {
        return webClient.get()
                .uri(userInfoUri)
                .header("Authorization", "Bearer " + accessToken)
                .retrieve()
                .bodyToMono(NaverUserInfoResponse.class)
                .block();
    }
}
