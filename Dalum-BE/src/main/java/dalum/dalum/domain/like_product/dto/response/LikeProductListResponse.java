package dalum.dalum.domain.like_product.dto.response;

import lombok.Builder;

import java.util.List;

@Builder
public record LikeProductListResponse(
        int totalPage,
        long totalElements,
        List<LikeProductResponse> likeProducts
) {
}
