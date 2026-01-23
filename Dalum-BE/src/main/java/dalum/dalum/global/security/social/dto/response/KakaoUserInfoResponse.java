package dalum.dalum.global.security.social.dto.response;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public record KakaoUserInfoResponse(
        Long id, // 카카오 고유 ID
        @JsonProperty("kakao_account") KakaoAccount kakaoAccount
) {

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record KakaoAccount(
            Profile profile,

            // 이메일 관련 필드
            String email,
            @JsonProperty("has_email") Boolean hasEmail,
            @JsonProperty("email_needs_agreement") Boolean emailNeedsAgreement
    ) {}

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Profile(
            String nickname
    ) {}
}
