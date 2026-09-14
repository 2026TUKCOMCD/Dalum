package dalum.dalum.domain.styling.service;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import dalum.dalum.domain.product.enums.LargeCategory;
import dalum.dalum.domain.product.repository.projection.ProductCandidateProjection;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.util.List;

/**
 * (largeCategory, style) 조합별 스타일링 추천 후보 풀 캐시.
 * 키 공간이 LargeCategory(7종) x style(최대 7종, null 포함)으로 최대 49개로 고정돼있어
 * 무한정 커지지 않음. 그래도 t3.large(2vCPU/8GB) 앱 컨테이너 메모리 예산 안에서
 * 안전하게 동작하도록 weigher로 실측 바이트 기준 상한을 건다.
 * (자세한 산정 근거: Obsidian capstone/스타일링 추천 후보풀 캐싱 아키텍처.md)
 */
@Component
public class CandidatePoolCache {

    private static final long MAX_WEIGHT_BYTES = 150L * 1024 * 1024; // 150MB
    private static final Duration TTL = Duration.ofHours(24);
    private static final int ENTRY_OVERHEAD_BYTES = 64;

    private final Cache<String, List<ProductCandidateProjection>> cache = Caffeine.newBuilder()
            .maximumWeight(MAX_WEIGHT_BYTES)
            .weigher((String key, List<ProductCandidateProjection> value) -> estimateWeight(value))
            .expireAfterWrite(TTL)
            .build();

    public String buildKey(LargeCategory largeCategory, String style) {
        return largeCategory.name() + "|" + (style == null ? "" : style.toLowerCase());
    }

    public List<ProductCandidateProjection> get(String key) {
        return cache.getIfPresent(key);
    }

    public void put(String key, List<ProductCandidateProjection> candidates) {
        cache.put(key, candidates);
    }

    private static int estimateWeight(List<ProductCandidateProjection> candidates) {
        long totalBytes = candidates.stream()
                .mapToLong(CandidatePoolCache::estimateEntryBytes)
                .sum();
        return (int) Math.min(totalBytes, Integer.MAX_VALUE);
    }

    private static long estimateEntryBytes(ProductCandidateProjection candidate) {
        long bytes = ENTRY_OVERHEAD_BYTES;
        String materialVectorJson = candidate.getMaterialVectorJson();
        String dominantColorsJson = candidate.getDominantColorsJson();
        if (materialVectorJson != null) bytes += materialVectorJson.length();
        if (dominantColorsJson != null) bytes += dominantColorsJson.length();
        return bytes;
    }
}
