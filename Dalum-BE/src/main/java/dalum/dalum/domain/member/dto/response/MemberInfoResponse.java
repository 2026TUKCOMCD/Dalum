package dalum.dalum.domain.member.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

@Builder
public record MemberInfoResponse(
        @Schema(description = "회원 ID", example = "1")
        Long memberId,

        @Schema(description = "닉네임", example = "화려한 카피바라")
        String nickname,

        @Schema(description = "로그인 타입", example = "KAKAO")
        String loginType
) {
}
