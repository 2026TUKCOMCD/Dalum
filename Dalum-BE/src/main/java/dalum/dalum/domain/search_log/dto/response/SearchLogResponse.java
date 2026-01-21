package dalum.dalum.domain.search_log.dto.response;

import lombok.Builder;

import java.time.LocalDateTime;

@Builder
public record SearchLogResponse(
        Long searchLogId,
        String inputImageUrl,
        LocalDateTime searchTime)
{
}
