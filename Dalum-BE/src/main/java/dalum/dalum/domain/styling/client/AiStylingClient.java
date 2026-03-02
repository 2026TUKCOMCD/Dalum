package dalum.dalum.domain.styling.client;

import dalum.dalum.domain.styling.client.dto.AiRecommendRequest;
import dalum.dalum.domain.styling.client.dto.AiRecommendedItem;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;
import java.util.Map;

@Component
@RequiredArgsConstructor
public class AiStylingClient {

    private final WebClient webClient;

    @Value("${ai.server.url}")
    private String aiServerUrl;

    public Map<String, List<AiRecommendedItem>> recommend(AiRecommendRequest request) {
        return webClient.post()
                .uri(aiServerUrl + "/api/v1/styling/recommend")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(request)
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<Map<String, List<AiRecommendedItem>>>() {})
                .block();
    }
}
