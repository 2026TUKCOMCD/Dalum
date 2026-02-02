package dalum.dalum.domain.search_log.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;

import java.util.List;

@Builder
public record SearchLogListResponse(

        @Schema(description = "총 페이지 수", example = "5")
        int totalPage,

        @Schema(description = "총 검색 로그 수", example = "50")
        long totalElements,

        @Schema(description = "검색 로그 리스트")
        List<SearchLogResponse> searchLogs
) {
}
