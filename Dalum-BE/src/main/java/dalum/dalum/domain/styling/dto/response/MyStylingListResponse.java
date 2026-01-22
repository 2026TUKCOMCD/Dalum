package dalum.dalum.domain.styling.dto.response;

import lombok.Builder;

import java.util.List;

@Builder
public record MyStylingListResponse(
        List<MyStylingResponse> stylings
) {
}
