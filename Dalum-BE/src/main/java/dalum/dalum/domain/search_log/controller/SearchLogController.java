package dalum.dalum.domain.search_log.controller;

import dalum.dalum.domain.search_log.dto.response.SearchLogListResponse;
import dalum.dalum.domain.search_log.exception.code.SearchLogSuccessCode;
import dalum.dalum.domain.search_log.service.SearchLogService;
import dalum.dalum.global.apipayload.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1")
public class SearchLogController {

    private final SearchLogService searchLogService;

    @Operation(summary = "내 검색 기록 조회", description = "마이페이지에서 내 검색 히스토리를 페이징하여 조회합니다.")
    @GetMapping("/me/search-logs")
    public ApiResponse<SearchLogListResponse> getSearchLog(
            Long memberId,
            @Parameter(description = "페이지 번호 (1부터 시작)")
            @RequestParam(defaultValue = "1") Integer page,

            @Parameter(description = "한 페이지에 보여줄 개수")
            @RequestParam(defaultValue = "10") Integer size
    ) {
        memberId = (memberId == null) ? 1L : memberId;

        SearchLogListResponse response = searchLogService.getSearchLog(memberId, page, size);

        return ApiResponse.success(SearchLogSuccessCode.OK, response);
    }
}
