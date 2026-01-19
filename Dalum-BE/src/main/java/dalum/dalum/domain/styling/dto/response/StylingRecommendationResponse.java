package dalum.dalum.domain.styling.dto.response;

import dalum.dalum.domain.product.dto.response.ProductDto;
import lombok.Builder;

import java.time.LocalDateTime;
import java.util.List;

@Builder
public record StylingRecommendationResponse(
        Long stylingId,
        ProductDto mainItem,
        List<RecommendationCategoryResponse> resultItems,
        LocalDateTime createdAt
) {
}
