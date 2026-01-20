package dalum.dalum.domain.member.converter;

import dalum.dalum.domain.member.dto.response.MemberInfoResponse;
import dalum.dalum.domain.member.entity.Member;
import org.springframework.stereotype.Component;

@Component
public class MemberConverter {

    public MemberInfoResponse toMemberInfoResponse(Member member) {
        return MemberInfoResponse.builder()
                .memberId(member.getId())
                .nickname(member.getNickname())
                .loginType(member.getSocialType().name())
                .build();
    }
}
