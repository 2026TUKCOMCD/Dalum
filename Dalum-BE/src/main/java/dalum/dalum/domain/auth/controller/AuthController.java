package dalum.dalum.domain.auth.controller;

import dalum.dalum.domain.auth.dto.request.SocialLoginRequest;
import dalum.dalum.domain.auth.dto.response.AuthTokenResponse;
import dalum.dalum.domain.auth.exception.code.AuthSuccessCode;
import dalum.dalum.domain.auth.service.AuthService;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.enums.SocialType;
import dalum.dalum.domain.member.repository.MemberRepository;
import dalum.dalum.global.apipayload.ApiResult;
import dalum.dalum.global.redis.RedisUtil;
import dalum.dalum.global.security.jwt.JwtTokenProvider;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "Auth", description = "인증 관련 API")
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/auth")
public class AuthController {

    private final AuthService authService;
    private final MemberRepository memberRepository;
    private final JwtTokenProvider jwtTokenProvider;
    private final RedisUtil redisUtil;

    @Operation(summary = "소셜 로그인/회원가입", description = "Provider(kakao, naver, google)에 따라 소셜 로그인을 진행하고 토큰을 발급합니다.")
    @ApiResponse(responseCode = "AUTH_200_1", description = "로그인 성공입니다.")
    @PostMapping("/login/{provider}")

    public ApiResult<AuthTokenResponse> login(
            @PathVariable String provider,
            @RequestBody @Valid SocialLoginRequest request
    ) {
        AuthTokenResponse response = authService.socialLogin(
                provider,
                request.authorizationCode(),
                request.redirectUri()
        );

        return ApiResult.success(AuthSuccessCode.OK, response);
    }

    @Operation(summary = "마스터 토큰 발급", description = "테스트 유저 생성")
    @ApiResponse(responseCode = "AUTH_200_1", description = "테스트 로그인 성공입니다.")
    @PostMapping("/test-login")
    public ApiResult<AuthTokenResponse> testLogin() {
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

        redisUtil.setDataExpire("RT :" + testMember.getId(), refreshToken, 100000000000L);

        return ApiResult.success(AuthSuccessCode.OK,
                AuthTokenResponse.builder()
                        .grantType("Bearer")
                        .accessToken(accessToken)
                        .refreshToken(refreshToken)
                        .accessTokenExpiresIn(100000000000L)
                        .build());
    }

    @Operation(summary = "엑세스 토큰 재발급 API", description = "리프레시 토큰으로 엑세스 토큰을 재발급합니다.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "AUTH_200_1", description = "토큰 재발급 성공입니다"),
            @ApiResponse(responseCode = "AUTH_401_1", description = "유효하지 않은 토큰입니다."),
            @ApiResponse(responseCode = "AUTH_401_2", description = "만료된 토큰입니다."),
            @ApiResponse(responseCode = "AUTH404_1", description = "토큰을 찾을 수 없습니다."),
            @ApiResponse(responseCode = "MEMBER_404_1", description = "회원을 찾을 수 없습니다.")

    })
    @PostMapping("/reissue")
    public ApiResult<AuthTokenResponse> reissueAccessToken(
            @RequestHeader("Refresh-Token") String refreshToken
    ) {
        String token = refreshToken.startsWith("Bearer ")
                ? refreshToken.substring(7)
                : refreshToken;

        AuthTokenResponse response = authService.refreshAccessToken(token);

        return ApiResult.success(AuthSuccessCode.REISSUE, response);
    }

    @Operation(summary = "로그아웃 API", description = "엑세스 토큰과 리프레시 토큰을 모두 만료 처리합니다.")
    @ApiResponse(responseCode = "AUTH_200_3", description = "로그아웃 성공입니다.")
    @PostMapping("/logout")
    public ApiResult<Void> logout(HttpServletRequest request) {
        String accessToken = jwtTokenProvider.resolveToken(request);

        authService.logout(accessToken);

        return ApiResult.success(AuthSuccessCode.LOGOUT, null);
    }

    @Operation(summary = "회원 탈퇴 API", description = "회원 탈퇴를 진행합니다.")
    @ApiResponse(responseCode = "AUTH_200_4", description = "회원 탈퇴 성공입니다.")
    @DeleteMapping("/withdraw")
    public ApiResult<Void> withdraw(HttpServletRequest request) {
        String accessToken = jwtTokenProvider.resolveToken(request);
        Long memberId = Long.parseLong(jwtTokenProvider.getAuthentication(accessToken).getName());

        authService.withdraw(memberId, accessToken);

        return ApiResult.success(AuthSuccessCode.WITHDRAW, null);
    }
}
