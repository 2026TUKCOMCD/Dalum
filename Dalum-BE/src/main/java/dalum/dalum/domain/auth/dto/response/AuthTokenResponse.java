package dalum.dalum.domain.auth.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

@Builder
public record AuthTokenResponse(
        @Schema(description = "그랜트 타입", example = "Bearer")
        String grantType,
        @Schema(description = "액세스 토큰", example = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        String accessToken,
        @Schema(description = "리프레시 토큰", example = "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...")
        String refreshToken,
        @Schema(description = "액세스 토큰 만료 시간(초)", example = "3600")
        Long accessTokenExpiresIn
) {
}
