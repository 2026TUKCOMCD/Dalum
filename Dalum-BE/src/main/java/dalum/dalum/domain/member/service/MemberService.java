package dalum.dalum.domain.member.service;

import dalum.dalum.domain.member.converter.MemberConverter;
import dalum.dalum.domain.member.dto.response.MemberInfoResponse;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.exception.MemberException;
import dalum.dalum.domain.member.exception.code.MemberErrorCode;
import dalum.dalum.domain.member.repository.MemberRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class MemberService {

    private final MemberRepository memberRepository;
    private final MemberConverter memberConverter;

    public MemberInfoResponse getMemberResponse(Long memberId) {

        Member member = memberRepository.findById(memberId).orElseThrow(
                () -> new MemberException(MemberErrorCode.NOT_FOUND));

        MemberInfoResponse response = memberConverter.toMemberInfoResponse(member);

        return response;
    }
}
