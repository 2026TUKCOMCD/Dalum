package dalum.dalum.domain.auth.service;

import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.enums.SocialType;
import dalum.dalum.domain.member.repository.MemberRepository;
import dalum.dalum.global.security.jwt.JwtTokenProvider;
import dalum.dalum.global.security.kakao.dto.response.KakaoUserInfoResponse;
import dalum.dalum.global.security.kakao.service.KakaoAuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final KakaoAuthService kakaoAuthService;
    private final MemberRepository memberRepository;
    private final JwtTokenProvider jwtTokenProvider;

    @Transactional
    public String kakaoLogin(String code) {
        // 1. 토큰 발급
        String kakaoAccessToken = kakaoAuthService.getAccessToken(code);

        // 2. 유저 정보 조회 (이미지 없이 닉네임/이메일만 옴)
        KakaoUserInfoResponse kakaoUserInfo = kakaoAuthService.getUserInfo(kakaoAccessToken);

        // 3. 이메일 추출 및 예외 처리 (선택 동의 대비)
        String email = kakaoUserInfo.kakaoAccount().email();

        // 이메일이 없는 경우 (동의 안 함 등) -> 카카오 ID 기반 임시 이메일 생성
        if (email == null || email.isBlank()) {
            email = kakaoUserInfo.id() + "@kakao.user";
        }

        // 4. 회원가입 or 로그인
        String finalEmail = email;
        Member member = memberRepository.findByEmail(finalEmail)
                .orElseGet(() -> registerKakaoUser(kakaoUserInfo, finalEmail));

        // 5. JWT 토큰 발행
        return jwtTokenProvider.createAccessToken(member.getId());
    }

    private Member registerKakaoUser(KakaoUserInfoResponse userInfo, String email) {
        return memberRepository.save(Member.builder()
                .email(email) // 이메일 저장
                .nickname(userInfo.kakaoAccount().profile().nickname()) // 닉네임 저장
                .socialType(SocialType.KAKAO)
                .build());
    }
}