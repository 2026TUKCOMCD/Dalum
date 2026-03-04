package dalum.dalum.domain.auth.service;

import dalum.dalum.domain.auth.dto.response.AuthTokenResponse;
import dalum.dalum.domain.auth.exception.AuthException;
import dalum.dalum.domain.auth.exception.code.AuthErrorCode;
import dalum.dalum.domain.dupe_product.repository.DupeProductRepository;
import dalum.dalum.domain.like_product.repository.LikeProductRepository;
import dalum.dalum.domain.member.exception.MemberException;
import dalum.dalum.domain.member.exception.code.MemberErrorCode;
import dalum.dalum.domain.member.repository.MemberRepository;
import dalum.dalum.domain.search_log.entity.SearchLog;
import dalum.dalum.domain.search_log.repository.SearchLogRepository;
import dalum.dalum.domain.styling.repository.StylingRepository;
import dalum.dalum.global.redis.RedisUtil;
import dalum.dalum.global.security.jwt.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final MemberRepository memberRepository;
    private final JwtTokenProvider jwtTokenProvider;
    private final RedisUtil redisUtil;
    private final LikeProductRepository likeProductRepository;
    private final SearchLogRepository searchLogRepository;
    private final DupeProductRepository dupeProductRepository;

    @Value("${jwt.access-expiration}")
    private Long accessExpiration;

    @Transactional
    public AuthTokenResponse refreshAccessToken(String refreshToken) {
        if (!jwtTokenProvider.validateToken(refreshToken)) {
            throw new AuthException(AuthErrorCode.NOT_FOUND);
        }

        Long memberId = jwtTokenProvider.getMemberIdFromToken(refreshToken);

        String storedRefreshToken = redisUtil.getData("RT :" + memberId);
        if (storedRefreshToken == null) {
            throw new AuthException(AuthErrorCode.EXPIRED_TOKEN);
        }

        if (!refreshToken.equals(storedRefreshToken)) {
            throw new AuthException(AuthErrorCode.INVALID_TOKEN);
        }

        if (!memberRepository.existsById(memberId)) {
            throw new MemberException(MemberErrorCode.NOT_FOUND);
        }

        String newAccessToken = jwtTokenProvider.createAccessToken(memberId);

        return AuthTokenResponse.builder()
                .grantType("Bearer")
                .accessToken(newAccessToken)
                .refreshToken(refreshToken)
                .accessTokenExpiresIn(accessExpiration)
                .build();
        }


    @Transactional
    public void logout(String accessToken) {
        long memberId = Long.parseLong(jwtTokenProvider.getAuthentication(accessToken).getName());

        // Redis에서 해당 회원의 refresh token 삭제
        if (redisUtil.getData("RT :" + memberId) != null) {
            redisUtil.deleteData("RT :" + memberId);
        }

        // Access Token의 남은 유효시간 계산
        Long expiration = jwtTokenProvider.getExpiration(accessToken);

        // 블랙리스트에 추가 (Key: AccessToken, Value: "logout")
        if (expiration > 0) {
            redisUtil.setDataExpire(accessToken, "logout", expiration);
        }
    }

    @Transactional
    public void withdraw(Long memberId, String accessToken) {
        logout(accessToken);

        if (!memberRepository.existsById(memberId)) {
            throw new MemberException(MemberErrorCode.NOT_FOUND);
        }

        likeProductRepository.deleteByMemberId(memberId);

        List<SearchLog> memberLogs = searchLogRepository.findByMemberId(memberId);

        for (SearchLog log : memberLogs) {
            dupeProductRepository.deleteBySearchLog(log);
        }

        searchLogRepository.deleteAll(memberLogs);
        memberRepository.deleteById(memberId);
    }
}