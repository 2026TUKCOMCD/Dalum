package dalum.dalum.global.security.social.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;

public record NaverTokenResponse(
        @JsonProperty("access_token") String accessToken,
        @JsonProperty("refresh_token") String refreshToken,
        @JsonProperty("token_type") String tokenType,
        @JsonProperty("expires_in") Integer expiresIn
) {
}
