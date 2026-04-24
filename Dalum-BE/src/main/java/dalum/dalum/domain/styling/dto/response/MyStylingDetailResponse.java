package dalum.dalum.domain.styling.dto.response;

import dalum.dalum.domain.product.enums.LargeCategory;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

import java.time.LocalDateTime;
import java.util.List;

@Builder
public record MyStylingDetailResponse(

        @Schema(description = "스타일링 ID", example = "1")
        Long stylingId,

        @Schema(description = "스타일링 생성일", example = "2024-06-15T14:30:00")
        LocalDateTime createdAt,

        @Schema(description = "스타일링 이름", example = "2026-01-31")
        String name,

        @Schema(description = "메인 상품 정보")
        MainProductDetail mainProduct,

        @Schema(description = "추천 상품 정보")
        List<RecommendedItemDetail> items
) {

    // 메인 상품에 대한 DTO
    @Builder
    public record MainProductDetail(
            Long productId,
            String name,
            String brand,
            double discountRate,
            int discountPrice,
            String imageUrl,
            String purchaseLink,
            boolean isLiked
    ) {}

    // 추천 상품에 대한 DTO
    @Builder
    public record RecommendedItemDetail(
            Long productId,
            LargeCategory category, // "BOTTOM", "SHOES" 등 Enum
            String name,
            String brand,
            double discountRate,
            int discountPrice,
            String imageUrl,
            String purchaseLink,
            boolean isLiked
    ) {}


}
