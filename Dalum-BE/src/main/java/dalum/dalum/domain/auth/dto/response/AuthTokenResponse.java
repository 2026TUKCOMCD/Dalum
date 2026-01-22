package dalum.dalum.domain.auth.dto.response;

import lombok.Builder;

@Builder
public record AuthTokenResponse(
        String grantType,
        String accessToken,
        String refreshToken,
        Long accessTokenExpiresIn
) {
}
