package dalum.dalum.domain.styling.dto.response;

import dalum.dalum.domain.product.dto.response.ProductDto;
import lombok.Builder;

import java.time.LocalDateTime;
import java.util.List;

@Builder
public record MyStylingResponse(
        Long stylingId,
        LocalDateTime createdAt,
        List<ProductDto> products
) {
}
