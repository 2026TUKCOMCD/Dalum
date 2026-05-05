package dalum.dalum.domain.dupe_product.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

@Builder
public record DupeProductDto(
        @Schema(description = "상품 ID", example = "1")
        Long productId,

        @Schema(description = "상품명", example = "나이키 에어포스1")
        String name,

        @Schema(description = "브랜드명", example = "나이키")
        String brand,

        @Schema(description = "대분류", example = "SHOES")
        String category,

        @Schema(description = "할인율", example = "50.0")
        Double discountRate,

        @Schema(description = "가격", example = "100000")
        Integer price,

        @Schema(description = "이미지 주소", example = "https://example.com/image.jpg")
        String imageUrl,

        @Schema(description = "구매링크", example = "https://musinsa.com")
        String purchaseUrl,

        @Schema(description = "좋아요 여부", example = "true")
        boolean isLiked,

        @Schema(description = "색상 유사도", example = "0.50")
        Double colorScore,

        @Schema(description = "소재 유사도", example = "0.99")
        Double materialScore,

        @Schema(description = "디자인 유사도", example = "0.74")
        Double designScore,

        @Schema(description = "종합 유사도", example = "0.95")
        Double totalScore
) {
}