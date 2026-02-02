package dalum.dalum.domain.auth.service;

import dalum.dalum.domain.auth.dto.response.AuthTokenResponse;
import dalum.dalum.domain.auth.exception.AuthException;
import dalum.dalum.domain.auth.exception.code.AuthErrorCode;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.enums.SocialType;
import dalum.dalum.domain.member.exception.MemberException;
import dalum.dalum.domain.member.exception.code.MemberErrorCode;
import dalum.dalum.domain.member.repository.MemberRepository;
import dalum.dalum.global.security.jwt.JwtTokenProvider;
import dalum.dalum.global.security.social.dto.response.GoogleUserInfoResponse;
import dalum.dalum.global.security.social.dto.response.KakaoUserInfoResponse;
import dalum.dalum.global.security.social.dto.response.NaverUserInfoResponse;
import dalum.dalum.global.security.social.service.GoogleAuthService;
import dalum.dalum.global.security.social.service.KakaoAuthService;
import dalum.dalum.global.security.social.service.NaverAuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final MemberRepository memberRepository;
    private final JwtTokenProvider jwtTokenProvider;
    private final KakaoAuthService kakaoAuthService;
    private final GoogleAuthService googleAuthService;
    private final NaverAuthService naverAuthService;

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
                member = getOrCreateMemberKakao(userInfo);
            }
            case "naver" -> {
                String accessToken = naverAuthService.getAccessToken(code);
                NaverUserInfoResponse userInfo = naverAuthService.getUserInfo(accessToken);
                member = getOrCreateMemberNaver(userInfo);
            }
            case "google" -> {
                String accessToken = googleAuthService.getAccessToken(code, redirectUri);
                GoogleUserInfoResponse userInfo = googleAuthService.getUserInfo(accessToken);
                member = getOrCreateMemberGoogle(userInfo);
            }
            default -> throw new IllegalArgumentException("지원하지 않는 소셜 로그인입니다: " + provider);
        }

        // 2. JWT 토큰 발급 (Access + Refresh)
        String accessToken = jwtTokenProvider.createAccessToken(member.getId());
        String refreshToken = jwtTokenProvider.createRefreshToken(member.getId());

        member.updateRefreshToken(refreshToken);
        memberRepository.save(member);

        // 3. 응답 DTO 생성
        return AuthTokenResponse.builder()
                .grantType("Bearer")
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .accessTokenExpiresIn(accessExpiration)
                .build();
    }

    @Transactional
    public AuthTokenResponse refreshAccessToken(String refreshToken) {
        if (!jwtTokenProvider.validateToken(refreshToken)) {
            throw new AuthException(AuthErrorCode.NOT_FOUND);
        }

        Long memberId = jwtTokenProvider.getMemberIdFromToken(refreshToken);

        Member member = memberRepository.findById(memberId).orElseThrow(
                () -> new MemberException(MemberErrorCode.NOT_FOUND));


        if (!refreshToken.equals(member.getRefreshToken())) {
            throw new AuthException(AuthErrorCode.INVALID_TOKEN);
        }

            String newAccessToken = jwtTokenProvider.createAccessToken(memberId);

            return AuthTokenResponse.builder()
                    .grantType("Bearer")
                    .accessToken(newAccessToken)
                    .refreshToken(refreshToken)
                    .accessTokenExpiresIn(accessExpiration)
                    .build();
        }

        // 카카오 회원가입 로직
        private Member getOrCreateMemberKakao(KakaoUserInfoResponse userInfo){
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
                            .socialType(SocialType.KAKAO)
                            .socialId(socialId)
                            .build()));
    }

        private Member getOrCreateMemberGoogle (GoogleUserInfoResponse userInfo){
            String email = userInfo.email(); // 구글은 이메일이 무조건 있음 (scope에 email 포함 시)

            String socialId = String.valueOf(userInfo.sub());

            return memberRepository.findByEmail(email)
                    .orElseGet(() -> memberRepository.save(Member.builder()
                            .email(email)
                            .nickname(userInfo.name())
                            .socialType(SocialType.GOOGLE)
                            .socialId(socialId)
                            .build()));
        }


        private Member getOrCreateMemberNaver (NaverUserInfoResponse userInfo){
            NaverUserInfoResponse.Response response = userInfo.response();
            String email = response.email();

            if (email == null || email.isBlank()) {
                email = response.id() + "@naver.user";
            }

            String finalEmail = email;
            return memberRepository.findByEmail(finalEmail)
                    .orElseGet(() -> memberRepository.save(Member.builder()
                            .email(finalEmail)
                            .nickname(response.nickname())
                            .socialType(SocialType.NAVER)
                            .socialId(response.id())
                            .build()));
    }
}