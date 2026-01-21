package dalum.dalum.domain.search_log.dto.response;

import lombok.Builder;

@Builder
public record SearchConditionDto(
        int minPrice,
        int maxPrice
) {
}
