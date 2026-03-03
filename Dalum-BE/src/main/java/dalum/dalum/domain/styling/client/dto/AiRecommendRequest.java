package dalum.dalum.domain.styling.client.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

public record AiRecommendRequest(
        @JsonProperty("input") AiInputItem input,
        @JsonProperty("candidates") List<AiCandidateItem> candidates,
        @JsonProperty("top_k") int topK,
        @JsonProperty("score_threshold") double scoreThreshold
) {
}