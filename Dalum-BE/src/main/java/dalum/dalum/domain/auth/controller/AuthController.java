package dalum.dalum.domain.auth.controller;

import dalum.dalum.domain.auth.dto.request.SocialLoginRequest;
import dalum.dalum.domain.auth.dto.response.AuthTokenResponse;
import dalum.dalum.domain.auth.exception.code.AuthSuccessCode;
import dalum.dalum.domain.auth.service.AuthService;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.enums.SocialType;
import dalum.dalum.domain.member.repository.MemberRepository;
import dalum.dalum.global.apipayload.ApiResponse;
import dalum.dalum.global.security.jwt.JwtTokenProvider;
import io.swagger.v3.oas.annotations.Operation;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/auth")
public class AuthController {

    private final AuthService authService;
    private final MemberRepository memberRepository;
    private final JwtTokenProvider jwtTokenProvider;

    @Operation(summary = "소셜 로그인/회원가입", description = "Provider(kakao, naver, google)에 따라 소셜 로그인을 진행하고 토큰을 발급합니다.")
    @PostMapping("/login/{provider}")
    public ApiResponse<AuthTokenResponse> login(
            @PathVariable String provider,
            @RequestBody @Valid SocialLoginRequest request
    ) {
        AuthTokenResponse response = authService.socialLogin(
                provider,
                request.authorizationCode(),
                request.redirectUri()
        );

        return ApiResponse.success(AuthSuccessCode.OK, response);
    }

    @Operation(summary = "마스터 토큰 발급", description = "테스트 유저 생성")
    @PostMapping("/test-login")
    public ApiResponse<AuthTokenResponse> testLogin() {
        // 테스트 회원이 없으면 생성
        Member testMember = memberRepository.findByEmail("test@test.com")
                .orElseGet(() -> memberRepository.save(Member.builder()
                        .email("test@test.com")
                        .nickname("테스트유저")
                        .socialType(SocialType.TEST)
                        .socialId("test-user-1")
                        .build()));


        String accessToken = jwtTokenProvider.createAccessToken(testMember.getId());
        String refreshToken = jwtTokenProvider.createRefreshToken(testMember.getId());

        return ApiResponse.success(AuthSuccessCode.OK,
                AuthTokenResponse.builder()
                        .grantType("Bearer")
                        .accessToken(accessToken)
                        .refreshToken(refreshToken)
                        .accessTokenExpiresIn(100000000000L)
                        .build());
    }
}
