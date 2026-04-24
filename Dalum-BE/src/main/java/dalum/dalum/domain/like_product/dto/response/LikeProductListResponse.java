package dalum.dalum.domain.like_product.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

import java.util.List;

@Builder
public record LikeProductListResponse(
        @Schema(description = "총 페이지 수", example = "10")
        int totalPage,

        @Schema(description = "총 상품 수", example = "100")
        long totalElements,

        @Schema(description = "좋아요 상품 리스트")
        List<LikeProductResponse> likeProducts
) {
}
