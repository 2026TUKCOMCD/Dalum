package dalum.dalum.domain.like_product.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

@Builder
public record LikeProductResponse(
        @Schema(description = "상품 ID", example = "1")
        Long productId,

        @Schema(description = "상품명", example = "나이키 에어포스1")
        String name,

        @Schema(description = "할인율", example = "20.0")
        @JsonProperty("discount_rate") // JSON 키값 고정
        double discountRate,

        @Schema(description = "할인 가격", example = "80000")
        @JsonProperty("discount_price")
        int discountPrice,

        @Schema(description = "이미지 주소", example = "https://example.com/image.jpg")
        String imageUrl,

        @Schema(description = "구매링크", example = "https://musinsa.com")
        @JsonProperty("purchase_link")
        String purchaseLink,

        @Schema(description = "좋아요 여부", example = "true")
        boolean isLiked // 항상 true
) {
}
