package dalum.dalum.domain.like_product.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;

@Builder
public record LikeProductResponse(
        Long productId,
        String name,

        @JsonProperty("discount_rate") // JSON 키값 고정
        double discountRate,

        @JsonProperty("discount_price")
        int discountPrice,

        String imageUrl,

        @JsonProperty("purchase_link")
        String purchaseLink,

        boolean isLiked // 항상 true
) {
}
