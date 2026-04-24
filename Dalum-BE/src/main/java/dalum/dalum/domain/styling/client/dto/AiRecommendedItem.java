package dalum.dalum.domain.styling.client.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record AiRecommendedItem(
        @JsonProperty("product_id") Long productId,
        @JsonProperty("score") Double score
) {
}
