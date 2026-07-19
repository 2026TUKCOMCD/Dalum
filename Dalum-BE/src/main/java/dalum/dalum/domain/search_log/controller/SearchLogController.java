package dalum.dalum.domain.search_log.controller;

import dalum.dalum.domain.search_log.dto.response.SearchLogDetailResponse;
import dalum.dalum.domain.search_log.dto.response.SearchLogListResponse;
import dalum.dalum.domain.search_log.exception.code.SearchLogSuccessCode;
import dalum.dalum.domain.search_log.service.SearchLogService;
import dalum.dalum.global.apipayload.ApiResult;
import dalum.dalum.global.security.SecurityUtil;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "Search Log", description = "검색 기록 관련 API")
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1")
public class SearchLogController {

    private final SearchLogService searchLogService;

    @Operation(summary = "내 검색 기록 조회", description = "마이페이지에서 내 검색 히스토리를 페이징하여 조회합니다.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "SEARCH_LOG_200_1", description = "검색기록을 성공적으로 조회하였습니다."),
            @ApiResponse(responseCode = "MEMBER_404_1", description = "해당 유저를 찾지 못했습니다."),
    })
    @GetMapping("/me/search-logs")
    public ApiResult<SearchLogListResponse> getSearchLog(
            @Parameter(description = "페이지 번호 (1부터 시작)")
            @RequestParam(defaultValue = "1") Integer page,

            @Parameter(description = "한 페이지에 보여줄 개수")
            @RequestParam(defaultValue = "10") Integer size
    ) {

        Long memberId = SecurityUtil.getCurrentMemberId();

        SearchLogListResponse response = searchLogService.getSearchLog(memberId, page, size);

        return ApiResult.success(SearchLogSuccessCode.OK, response);
    }

    @Operation(summary = "내 검색 기록 상세 조회", description = "내 검색 히스토리를 상세 조회합니다.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "SEARCH_LOG_200_2", description = "검색기록 상세를 성공적으로 조회하였습니다."),
            @ApiResponse(responseCode = "MEMBER_404_1", description = "해당 유저를 찾지 못했습니다."),
            @ApiResponse(responseCode = "SEARCH_LOG_404_1", description = "해당 검색 기록을 찾지 못했습니다."),
    })
    @GetMapping("/me/search-logs/{searchId}")
    public ApiResult<SearchLogDetailResponse> getSearchLogDetail(
            @PathVariable("searchId") Long searchId
    ) {
        Long memberId = SecurityUtil.getCurrentMemberId();

        SearchLogDetailResponse response = searchLogService.getSearchLogDetail(memberId, searchId);

        return ApiResult.success(SearchLogSuccessCode.DETAIL_OK, response);
    }

    @Operation(summary = "듀프 검색기록 삭제", description = "특정 검색 기록을 삭제합니다.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "SEARCH_LOG_200_3", description = "검색기록이 성공적으로 삭제되었습니다."),
            @ApiResponse(responseCode = "SEARCH_LOG_403_1", description = "해당 검색기록에 접근 권한이 없습니다."),
            @ApiResponse(responseCode = "SEARCH_LOG_404_1", description = "해당 검색 기록을 찾지 못했습니다."),
    })
    @DeleteMapping("/me/search-logs/{searchId}")
    public ApiResult<Void> deleteSearchLog(
            @PathVariable("searchId") Long searchId
    ) {
        Long memberId = SecurityUtil.getCurrentMemberId();

        searchLogService.deleteSearchLog(memberId, searchId);

        return ApiResult.success(SearchLogSuccessCode.DELETED, null);
    }
}
