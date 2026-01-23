package dalum.dalum.domain.auth.controller;

import dalum.dalum.domain.auth.dto.request.SocialLoginRequest;
import dalum.dalum.domain.auth.dto.response.AuthTokenResponse;
import dalum.dalum.domain.auth.exception.code.AuthSuccessCode;
import dalum.dalum.domain.auth.service.AuthService;
import dalum.dalum.global.apipayload.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/auth")
public class AuthController {

    private final AuthService authService;

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
}
