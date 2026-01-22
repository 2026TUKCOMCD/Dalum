package dalum.dalum.domain.styling.dto.response;

import lombok.Builder;

import java.time.LocalDateTime;

@Builder
public record MyStylingResponse(
    Long stylingId,
    String imageUrl,
    LocalDateTime createdAt
) {
}
