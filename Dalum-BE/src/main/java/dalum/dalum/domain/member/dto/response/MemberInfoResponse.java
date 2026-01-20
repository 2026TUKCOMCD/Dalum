package dalum.dalum.domain.member.dto.response;

import lombok.Builder;

@Builder
public record MemberInfoResponse(
        Long memberId,
        String nickname,
        String loginType
) {
}
