package dalum.dalum.domain.product.dto.response;

import lombok.Builder;

@Builder
public record ProductDto(
        Long productId,
        String name,
        String brand,
        int price,
        String imageUrl,
        String purchaseUrl,
        double similarity,
        boolean isLiked
) {
}
