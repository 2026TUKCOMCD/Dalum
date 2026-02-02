package dalum.dalum.domain.search_log.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

import java.time.LocalDateTime;

@Builder
public record SearchLogResponse(

        @Schema(description = "검색 로그 ID", example = "1")
        Long searchLogId,

        @Schema(description = "이미지 URL", example = "https://example.com/image.jpg")
        String inputImageUrl,

        @Schema(description = "검색 시간", example = "2024-06-15T14:30:00")
        LocalDateTime searchTime
) {}
