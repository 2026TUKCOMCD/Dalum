package dalum.dalum.domain.search_log.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

@Builder
public record SearchConditionDto(
        @Schema(description = "최소가격", example = "10000")
        int minPrice,

        @Schema(description = "최대가격", example = "50000")
        int maxPrice
) {
}
