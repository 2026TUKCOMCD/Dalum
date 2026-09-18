package dalum.dalum.domain.styling.client.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Random;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * StylingServiceImpl 후보 상품 → AI 요청 변환 방식(리팩토링 전/후) 성능 비교용 마이크로 벤치마크.
 * DB/AI 서버 없이, "JSON 파싱 후 재직렬화(before)" vs "raw JSON 그대로 전달(after)" 만 비교한다.
 */
@DisplayName("AiCandidateItem raw-json passthrough 벤치마크")
class AiCandidatePayloadBenchmarkTest {

    private static final int CANDIDATE_COUNT = 5000;
    private static final int VECTOR_DIM = 128;
    private static final int WARMUP_TRIALS = 5;
    private static final int MEASURED_TRIALS = 20;

    private final ObjectMapper mapper = new ObjectMapper();

    // ---- 리팩토링 전(before) 방식을 재현한 로컬 레코드: List<Double>/List<Map>을 들고 있다가 직렬화 ----
    private record BeforeCandidateItem(
            @JsonProperty("id") Long id,
            @JsonProperty("category") String category,
            @JsonProperty("style") String style,
            @JsonProperty("material_vector") List<Double> materialVector,
            @JsonProperty("dominant_colors") List<Map<String, Object>> dominantColors
    ) {
    }

    private record BeforeRecommendRequest(
            @JsonProperty("input") AiInputItem input,
            @JsonProperty("candidates") List<BeforeCandidateItem> candidates,
            @JsonProperty("top_k") int topK,
            @JsonProperty("score_threshold") double scoreThreshold
    ) {
    }

    @Test
    @DisplayName("후보 5000개 기준 before(파싱+재직렬화) vs after(raw passthrough) 처리 시간 비교")
    void compareBeforeAndAfter() throws Exception {
        List<String> materialVectorJsons = new ArrayList<>(CANDIDATE_COUNT);
        List<String> dominantColorsJsons = new ArrayList<>(CANDIDATE_COUNT);
        generateFixtures(materialVectorJsons, dominantColorsJsons);

        AiInputItem input = new AiInputItem(List.of(0.1, 0.2, 0.3), null, "casual", "top");

        // JIT 워밍업 (측정에서 제외)
        for (int i = 0; i < WARMUP_TRIALS; i++) {
            runBefore(materialVectorJsons, dominantColorsJsons, input);
            runAfter(materialVectorJsons, dominantColorsJsons, input);
        }

        long beforeTotalNanos = 0;
        long afterTotalNanos = 0;
        for (int i = 0; i < MEASURED_TRIALS; i++) {
            beforeTotalNanos += runBefore(materialVectorJsons, dominantColorsJsons, input);
            afterTotalNanos += runAfter(materialVectorJsons, dominantColorsJsons, input);
        }

        double beforeAvgMs = (beforeTotalNanos / (double) MEASURED_TRIALS) / 1_000_000.0;
        double afterAvgMs = (afterTotalNanos / (double) MEASURED_TRIALS) / 1_000_000.0;
        double speedup = beforeAvgMs / afterAvgMs;

        System.out.println("==== AiCandidateItem 변환 방식 벤치마크 (후보 " + CANDIDATE_COUNT + "개, 벡터 차원 " + VECTOR_DIM + ") ====");
        System.out.printf("BEFORE (List<Double>/List<Map> 파싱 → 재직렬화) 평균: %.3f ms%n", beforeAvgMs);
        System.out.printf("AFTER  (raw JSON passthrough)             평균: %.3f ms%n", afterAvgMs);
        System.out.printf("speedup: %.2fx%n", speedup);

        assertThat(afterAvgMs).isLessThan(beforeAvgMs);
    }

    private long runBefore(List<String> materialVectorJsons, List<String> dominantColorsJsons, AiInputItem input) throws Exception {
        long start = System.nanoTime();

        List<BeforeCandidateItem> items = new ArrayList<>(CANDIDATE_COUNT);
        for (int i = 0; i < CANDIDATE_COUNT; i++) {
            List<Double> materialVector = mapper.readValue(materialVectorJsons.get(i), new TypeReference<>() {});
            List<Map<String, Object>> dominantColors = mapper.readValue(dominantColorsJsons.get(i), new TypeReference<>() {});
            items.add(new BeforeCandidateItem((long) i, "top", "casual", materialVector, dominantColors));
        }
        BeforeRecommendRequest request = new BeforeRecommendRequest(input, items, 3, 0.1);
        String json = mapper.writeValueAsString(request);

        long elapsed = System.nanoTime() - start;
        assertThat(json).isNotBlank();
        return elapsed;
    }

    private long runAfter(List<String> materialVectorJsons, List<String> dominantColorsJsons, AiInputItem input) throws Exception {
        long start = System.nanoTime();

        List<AiCandidateItem> items = new ArrayList<>(CANDIDATE_COUNT);
        for (int i = 0; i < CANDIDATE_COUNT; i++) {
            items.add(new AiCandidateItem((long) i, "top", "casual", materialVectorJsons.get(i), dominantColorsJsons.get(i)));
        }
        AiRecommendRequest request = new AiRecommendRequest(input, items, 3, 0.1);
        String json = mapper.writeValueAsString(request);

        long elapsed = System.nanoTime() - start;
        assertThat(json).isNotBlank();
        return elapsed;
    }

    private void generateFixtures(List<String> materialVectorJsons, List<String> dominantColorsJsons) throws Exception {
        Random random = new Random(42);
        for (int i = 0; i < CANDIDATE_COUNT; i++) {
            List<Double> vector = new ArrayList<>(VECTOR_DIM);
            for (int d = 0; d < VECTOR_DIM; d++) {
                vector.add(random.nextDouble());
            }
            materialVectorJsons.add(mapper.writeValueAsString(vector));

            List<Map<String, Object>> colors = List.of(
                    Map.of("colorName", "black", "ratio", 0.4),
                    Map.of("colorName", "white", "ratio", 0.35),
                    Map.of("colorName", "gray", "ratio", 0.25)
            );
            dominantColorsJsons.add(mapper.writeValueAsString(colors));
        }
    }
}
