package dalum.dalum.global.ai;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;

import java.io.IOException;
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
    public List<Long> getRecommendations(MultipartFile file, int topK) throws IOException {
        MultipartBodyBuilder builder = new MultipartBodyBuilder();
        builder.part("file", new ByteArrayResource(file.getBytes()) {
            @Override public String getFilename() { return file.getOriginalFilename(); }
        }).contentType(MediaType.parseMediaType(
                file.getContentType() != null ? file.getContentType() : "image/jpeg"));

        Map<String, Object> response = webClient.post()
                .uri(aiServerUrl + "/api/v1/dupe/search?top_k=" + topK)
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(BodyInserters.fromMultipartData(builder.build()))
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
                .map(item -> Long.valueOf(item.get("product_id").toString()))
                .toList();
    }
}