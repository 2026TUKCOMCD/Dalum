package dalum.dalum.global.ai;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.Duration;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class AiService {

    private final WebClient webClient;

    @Value("${ai.server.url}")
    private String aiServerUrl;

    @SuppressWarnings("unchecked")
    public List<AiDupeResult> getRecommendations(String s3Key, int topK) {
        Map<String, Object> requestBody = Map.of("s3_key", s3Key, "top_k", topK);

        Map<String, Object> response = webClient.post()
                .uri(aiServerUrl + "/api/v1/dupe/dupe-search")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(requestBody)
                .retrieve()
                .bodyToMono(Map.class)
                .timeout(Duration.ofSeconds(180))
                .block();

        if (response == null) return List.of();
        Map<String, Object> data = (Map<String, Object>) response.get("data");
        if (data == null) return List.of();
        List<Map<String, Object>> results = (List<Map<String, Object>>) data.get("results");
        if (results == null) return List.of();

        return results.stream()
                .map(item -> new AiDupeResult(
                        Long.valueOf(item.get("product_id").toString()),
                        toDouble(item.get("color_score")),
                        toDouble(item.get("material_score")),
                        toDouble(item.get("design_score")),
                        toDouble(item.get("total_score"))
                ))
                .toList();
    }

    private Double toDouble(Object value) {
        if (value == null) return null;
        return ((Number) value).doubleValue();
    }
}