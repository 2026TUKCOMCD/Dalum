package dalum.dalum.domain.styling.dto.response;

import lombok.Builder;

@Builder
public record StylingSaveResponse(
        Long stylingId
) {
}
