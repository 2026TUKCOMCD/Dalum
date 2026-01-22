package dalum.dalum.domain.auth.service;

import dalum.dalum.domain.auth.dto.response.AuthTokenResponse;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.enums.SocialType;
import dalum.dalum.domain.member.repository.MemberRepository;
import dalum.dalum.global.security.jwt.JwtTokenProvider;
import dalum.dalum.global.security.kakao.dto.response.KakaoUserInfoResponse;
import dalum.dalum.global.security.kakao.service.KakaoAuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final KakaoAuthService kakaoAuthService;
    private final MemberRepository memberRepository;
    private final JwtTokenProvider jwtTokenProvider;

    @Value("${jwt.access-expiration}")
    private Long accessExpiration;

    @Transactional
    public AuthTokenResponse socialLogin(String provider, String code, String redirectUri) {
        Member member = null;

        // 1. Provider에 따른 분기 처리
        switch (provider.toLowerCase()) {
            case "kakao" -> {
                // KakaoAuthService에 redirectUri도 같이 넘겨줘야 함!
                String accessToken = kakaoAuthService.getAccessToken(code, redirectUri);
                KakaoUserInfoResponse userInfo = kakaoAuthService.getUserInfo(accessToken);
                member = getOrCreateMember(userInfo, SocialType.KAKAO);
            }
            case "naver" -> {
                // member = naverAuthService.login(code, state);
                throw new IllegalArgumentException("네이버 로그인은 준비 중입니다.");
            }
            case "google" -> {
                // member = googleAuthService.login(code, redirectUri);
                throw new IllegalArgumentException("구글 로그인은 준비 중입니다.");
            }
            default -> throw new IllegalArgumentException("지원하지 않는 소셜 로그인입니다: " + provider);
        }

        // 2. JWT 토큰 발급 (Access + Refresh)
        String accessToken = jwtTokenProvider.createAccessToken(member.getId());
        String refreshToken = jwtTokenProvider.createRefreshToken(member.getId());


        // 3. 응답 DTO 생성
        return AuthTokenResponse.builder()
                .grantType("Bearer")
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .accessTokenExpiresIn(accessExpiration)
                .build();
    }

    // 회원가입 및 조회 공통 로직
    private Member getOrCreateMember(KakaoUserInfoResponse userInfo, SocialType loginType) {
        String email = userInfo.kakaoAccount().email();
        if (email == null || email.isBlank()) {
            email = userInfo.id() + "@kakao.user";
        }

        String socialId = String.valueOf(userInfo.id()); // 카카오 고유 ID

        String finalEmail = email;
        return memberRepository.findByEmail(finalEmail)
                .orElseGet(() -> memberRepository.save(Member.builder()
                        .email(finalEmail)
                        .nickname(userInfo.kakaoAccount().profile().nickname())
                        .socialType(loginType)
                        .socialId(socialId)
                        .build()));
    }
}