package dalum.dalum.domain.dupe_product.dto.response;

import dalum.dalum.domain.product.dto.response.ProductDto;
import lombok.Builder;

import java.util.List;

@Builder
public record DupeSearchResponse(
        Long searchLogId,
        int resultCount,
        List<ProductDto> products
) {

    public static DupeSearchResponse of(Long searchLogId, List<ProductDto> products) {
        return DupeSearchResponse.builder()
                .searchLogId(searchLogId)
                .resultCount(products.size())
                .products(products)
                .build();
    }
}
