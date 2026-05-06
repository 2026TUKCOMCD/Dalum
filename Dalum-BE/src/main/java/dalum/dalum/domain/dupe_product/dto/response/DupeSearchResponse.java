package dalum.dalum.domain.dupe_product.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

import java.util.List;

@Builder
public record DupeSearchResponse(
        @Schema(description = "검색 로그 ID", example = "1")
        Long searchLogId,

        @Schema(description = "검색 결과 수", example = "5")
        int resultCount,

        @Schema(description = "상품 리스트")
        List<DupeProductDto> products
) {

    public static DupeSearchResponse of(Long searchLogId, List<DupeProductDto> products) {
        return DupeSearchResponse.builder()
                .searchLogId(searchLogId)
                .resultCount(products.size())
                .products(products)
                .build();
    }
}
