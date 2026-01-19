package dalum.dalum.domain.like_product.dto.response;

public record LikeToggleResponse(
        boolean isLiked // true면 하트 채우기, false면 하트 비우기
) {
}
