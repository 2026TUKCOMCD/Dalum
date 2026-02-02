package dalum.dalum.domain.styling.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

import java.time.LocalDateTime;

@Builder
public record MyStylingResponse(

        @Schema(description = "스타일링 ID", example = "1")
        Long stylingId,

        @Schema(description = "메인 이미지", example = "https://example.com/styling.jpg")
        String imageUrl,

        @Schema(description = "스타일링 생성일", example = "2024-06-15T14:30:00")
        LocalDateTime createdAt
) {
}
