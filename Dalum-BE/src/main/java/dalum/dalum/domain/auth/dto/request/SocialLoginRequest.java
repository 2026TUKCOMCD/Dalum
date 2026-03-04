package dalum.dalum.domain.auth.dto.request;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;

public record SocialLoginRequest(
        @NotBlank
        @Schema(description = "인가코드", example = "authorization_code")
        String authorizationCode,

        @Schema(description = "리다이렉트 URI", example = "http://localhost:8080/oauth/callback/kakao")
        String redirectUri // 선택값
) {
}
