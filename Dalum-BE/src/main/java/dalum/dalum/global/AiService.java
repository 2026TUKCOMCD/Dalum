package dalum.dalum.global;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class AiService {

    private final WebClient webClient;

    @Value("${ai.server.url}")
    private String aiServerUrl;

    public List<Long> getDupeRecommendations(String imageUrl) {
        // AI 서버 호출
        AiDupeResponse response = webClient.post()
            .uri(aiServerUrl + "/api/v1/dupe/search-by-url")
            .bodyValue(Map.of("imageUrl", imageUrl))
            .retrieve()
            .bodyToMono(AiDupeResponse.class)
            .block();

        return response.getResults().stream()
            .map(AiDupeResponse.Result::getProductId)
            .toList();
    }
}