package dalum.dalum.domain.styling.dto.response;

import dalum.dalum.domain.product.dto.response.ProductDto;
import dalum.dalum.domain.product.enums.LargeCategory;
import lombok.Builder;

import java.util.List;

@Builder
public record RecommendationCategoryResponse(
    String category,
    List<ProductDto> products
) {
}
