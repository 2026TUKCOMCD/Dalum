package dalum.dalum.domain.member.service;

import dalum.dalum.domain.member.converter.MemberConverter;
import dalum.dalum.domain.member.dto.response.MemberInfoResponse;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.repository.MemberRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class MemberServiceTest {

    @Mock
    private MemberRepository memberRepository;

    @Mock
    private MemberConverter memberConverter;

    @InjectMocks
    private MemberService memberService;

    @Test
    @DisplayName("회원 정보 조회 성공")
    void testGetMemberResponseSuccess() {
        // Given
        Long memberId = 1L;
        Member testMember = Member.builder().id(memberId).build();
        MemberInfoResponse mockResponse = MemberInfoResponse.builder().memberId(memberId).build();

        when(memberRepository.findById(memberId))
                .thenReturn(Optional.of(testMember));
        when(memberConverter.toMemberInfoResponse(testMember))
                .thenReturn(mockResponse);

        // When
        MemberInfoResponse response = memberService.getMemberResponse(memberId);

        // Then
        assertThat(response).isNotNull();
        assertThat(response.memberId()).isEqualTo(memberId);
        verify(memberRepository, times(1)).findById(memberId);
        verify(memberConverter, times(1)).toMemberInfoResponse(testMember);
    }

}


