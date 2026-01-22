package dalum.dalum.domain.auth.dto.request;

import jakarta.validation.constraints.NotBlank;

public record SocialLoginRequest(
        @NotBlank String authorizationCode,
        String redirectUri // 선택값
) {
}
