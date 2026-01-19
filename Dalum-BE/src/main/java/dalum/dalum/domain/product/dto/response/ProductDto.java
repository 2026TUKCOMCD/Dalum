package dalum.dalum.domain.product.dto.response;

import dalum.dalum.domain.product.enums.LargeCategory;
import lombok.Builder;

@Builder
public record ProductDto(
        Long productId,
        String name,
        String brand,
        String category,
        int price,
        String imageUrl,
        String purchaseUrl,
        double similarity,
        boolean isLiked
) {
}
