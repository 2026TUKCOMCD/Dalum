package dalum.dalum.domain.styling.dto.response;

import dalum.dalum.domain.product.dto.response.ProductDto;
import dalum.dalum.domain.product.enums.LargeCategory;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

import java.util.List;

@Builder
public record RecommendationCategoryResponse(
        @Schema(description = "대분류 카테고리", example = "TOP")
        String category,

        @Schema(description = "추천 상품 리스트")
        List<ProductDto> products
) {
}
