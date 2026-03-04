package dalum.dalum.domain.styling.dto.response;

import dalum.dalum.domain.product.dto.response.ProductDto;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

import java.time.LocalDateTime;
import java.util.List;

@Builder
public record StylingRecommendationResponse(

        @Schema(description = "스타일링 ID", example = "1")
        Long stylingId,

        @Schema(description = "메인 아이템 정보")
        ProductDto mainItem,

        @Schema(description = "추천 카테고리 리스트")
        List<RecommendationCategoryResponse> resultItems,

        @Schema(description = "스타일링 생성일", example = "2024-06-15T14:30:00")
        LocalDateTime createdAt
) {
}
