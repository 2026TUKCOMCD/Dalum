package dalum.dalum.domain.styling.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

@Builder
public record StylingSaveResponse(
        @Schema(description = "스타일링 ID", example = "1")
        Long stylingId
) {
}
