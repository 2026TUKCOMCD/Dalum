package dalum.dalum.domain.like_product.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;

public record LikeToggleResponse(
        @Schema(description = "좋아요 상태", example = "true")
        boolean isLiked // true면 하트 채우기, false면 하트 비우기
) {
}
