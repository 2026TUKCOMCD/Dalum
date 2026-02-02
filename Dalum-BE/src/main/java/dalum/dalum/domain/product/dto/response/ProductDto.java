package dalum.dalum.domain.product.dto.response;

import dalum.dalum.domain.product.enums.LargeCategory;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

@Builder
public record ProductDto(
        @Schema(description = "상품 ID", example = "1")
        Long productId,

        @Schema(description = "상품명", example = "나이키 에어포스1")
        String name,

        @Schema(description = "브랜드명", example = "나이키")
        String brand,

        @Schema(description = "대분류", example = "SHOES")
        String category,

        @Schema(description = "가격", example = "100000")
        int price,

        @Schema(description = "이미지 주소", example = "https://example.com/image.jpg")
        String imageUrl,

        @Schema(description = "구매링크", example = "https://musinsa.com")
        String purchaseUrl,

        @Schema(description = "유사도", example = "0.85")
        double similarity,

        @Schema(description = "좋아요 여부", example = "true")
        boolean isLiked
) {
}
