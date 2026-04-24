package dalum.dalum.domain.styling.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

import java.util.List;

@Builder
public record MyStylingListResponse(

        @Schema(description = "스타일링 리스트")
        List<MyStylingResponse> stylings
) {
}
