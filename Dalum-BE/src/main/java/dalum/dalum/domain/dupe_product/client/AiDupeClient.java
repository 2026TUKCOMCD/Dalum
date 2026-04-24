package dalum.dalum.domain.dupe_product.client;

import dalum.dalum.domain.dupe_product.client.dto.AiDupeResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;

import java.io.IOException;
import java.util.List;

@Component
@RequiredArgsConstructor
public class AiDupeClient {

    private final WebClient webClient;

    @Value("${ai.server.url}")
    private String aiServerUrl;

    public List<Long> search(MultipartFile imageFile) throws IOException {
        MultipartBodyBuilder builder = new MultipartBodyBuilder();
        builder.part("file", imageFile.getResource());

        AiDupeResponse response = webClient.post()
                .uri(aiServerUrl + "/api/v1/dupe/search")
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(BodyInserters.fromMultipartData(builder.build()))
                .retrieve()
                .bodyToMono(AiDupeResponse.class)
                .block();

        return response.getData().getResults().stream()
                .map(AiDupeResponse.Result::getProductId)
                .toList();
    }
}
