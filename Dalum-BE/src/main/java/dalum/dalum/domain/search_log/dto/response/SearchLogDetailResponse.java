package dalum.dalum.domain.search_log.dto.response;

import dalum.dalum.domain.dupe_product.dto.response.DupeProductDto;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

import java.time.LocalDateTime;
import java.util.List;

@Builder
public record SearchLogDetailResponse(

        @Schema(description = "검색 로그 ID", example = "1")
        Long searchLogId,

        @Schema(description = "검색 날짜", example = "2024-06-15T14:30:00")
        LocalDateTime searchDate,

        @Schema(description = "브랜드명", example = "나이키")
        String brand,

        @Schema(description = "이미지 URL", example = "https://example.com/image.jpg")
        String imageUrl,

        @Schema(description = "검색 조건")
        SearchConditionDto conditions,

        @Schema(description = "검색 결과 상품 리스트")
        List<DupeProductDto> results

) {
}
