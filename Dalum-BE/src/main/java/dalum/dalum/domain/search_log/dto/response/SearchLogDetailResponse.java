package dalum.dalum.domain.search_log.dto.response;

import dalum.dalum.domain.product.dto.response.ProductDto;
import dalum.dalum.domain.product.entity.Product;
import lombok.Builder;

import java.time.LocalDateTime;
import java.util.List;

@Builder
public record SearchLogDetailResponse(
        Long searchLogId,
        LocalDateTime searchDate,
        String imageUrl,
        SearchConditionDto conditions,
        List<ProductDto> results

) {
}
