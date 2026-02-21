package dalum.dalum.global.security.oauth2;

import dalum.dalum.domain.member.enums.SocialType;
import dalum.dalum.global.redis.RedisUtil;
import dalum.dalum.global.security.jwt.JwtTokenProvider;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.repository.MemberRepository;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.client.authentication.OAuth2AuthenticationToken;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationSuccessHandler;
import org.springframework.stereotype.Component;
import org.springframework.web.util.UriComponentsBuilder;

import java.io.IOException;
import java.util.Map;

@Component
@RequiredArgsConstructor
public class OAuth2SuccessHandler extends SimpleUrlAuthenticationSuccessHandler {

    private final JwtTokenProvider jwtTokenProvider;
    private final MemberRepository memberRepository;
    private final RedisUtil redisUtil;

    @Value("${jwt.refresh-expiration}")
    private Long refreshExpiration;

    @Value("${app.oauth2.redirect-uri}")
    private String redirectUri;

    @Override
    public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response, Authentication authentication) throws IOException, ServletException {

        OAuth2AuthenticationToken token = (OAuth2AuthenticationToken) authentication;
        String provider = token.getAuthorizedClientRegistrationId();

        OAuth2User oAuth2User = token.getPrincipal();
        Map<String, Object> attributes = oAuth2User.getAttributes();

        String email = null;
        String name = null;
        String socialId = null;

        SocialType socialType = SocialType.valueOf(provider.toUpperCase());

        // 1. 소셜 회사별로 이메일, 이름 파싱하기
        if ("kakao".equals(provider)) {
            Map<String, Object> kakaoAccount = (Map<String, Object>) attributes.get("kakao_account");
            Map<String, Object> profile = (Map<String, Object>) kakaoAccount.get("profile");
            email = (String) kakaoAccount.get("email");
            name = (String) profile.get("nickname");
            socialId = String.valueOf(attributes.get("id"));
        } else if ("naver".equals(provider)) {
            Map<String, Object> responseMap = (Map<String, Object>) attributes.get("response");
            email = (String) responseMap.get("email");
            name = (String) responseMap.get("name");
            socialId = (String) responseMap.get("id");
        } else if ("google".equals(provider)) {
            email = (String) attributes.get("email");
            name = (String) attributes.get("name");
            socialId = (String) attributes.get("sub");
        }

        // 🚨 이메일이 없는 경우 (카카오 등에서 이메일 동의 안 한 경우 방어 로직)
        if (email == null || email.isBlank()) {
            email = socialId + "@" + provider + ".user";
        }

        // 2. DB에서 유저 찾기 or 없으면 회원가입
        String finalEmail = email;
        String finalName = name;
        String finalSocialId = socialId;

        Member member = memberRepository.findByEmail(finalEmail)
                .orElseGet(() -> {
                    Member newMember = Member.builder()
                            .email(finalEmail)
                            .nickname(finalName)
                            .socialType(socialType)
                            .socialId(finalSocialId)
                            .build();

                    return memberRepository.save(newMember);
                });

        String accessToken = jwtTokenProvider.createAccessToken(member.getId());

        String refreshToken = jwtTokenProvider.createRefreshToken(member.getId());
        redisUtil.setDataExpire("RT: " + member.getId(), refreshToken, refreshExpiration);

        String targetUrl = UriComponentsBuilder.fromUriString("http://localhost:5173/oauth/callback")
                .queryParam("accessToken", accessToken)
                .queryParam("refreshToken", refreshToken)
                .build().toUriString();

        getRedirectStrategy().sendRedirect(request, response, targetUrl);
    }
}