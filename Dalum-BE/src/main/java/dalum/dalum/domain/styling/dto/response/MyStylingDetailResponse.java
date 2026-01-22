package dalum.dalum.domain.styling.dto.response;

import dalum.dalum.domain.product.enums.LargeCategory;
import lombok.Builder;

import java.time.LocalDateTime;
import java.util.List;

@Builder
public record MyStylingDetailResponse(
        Long stylingId,
        LocalDateTime createdAt,
        String name,
        MainProductDetail mainProduct,
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
