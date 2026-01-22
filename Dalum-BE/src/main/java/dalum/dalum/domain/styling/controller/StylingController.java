package dalum.dalum.domain.styling.controller;

import dalum.dalum.domain.styling.dto.response.MyStylingDetailResponse;
import dalum.dalum.domain.styling.dto.response.MyStylingListResponse;
import dalum.dalum.domain.styling.dto.response.StylingRecommendationResponse;
import dalum.dalum.domain.styling.dto.response.StylingSaveResponse;
import dalum.dalum.domain.styling.exception.code.StylingSuccessCode;
import dalum.dalum.domain.styling.service.StylingService;
import dalum.dalum.domain.styling.service.StylingServiceImpl;
import dalum.dalum.global.apipayload.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1")
public class StylingController {

    private final StylingService stylingService;

    @Operation(summary = "스타일링 추천 API", description = "AI가 좋아요한 제품에대해 스타일링을 생성합니다.")
    @PostMapping("/stylings/recommend")
    public ApiResponse<StylingRecommendationResponse> recommendProducts(
            Long memberId, // @AuthenticationPrincipal
            Long targetProductId
    ) {
        memberId = (memberId == null) ? 1L : memberId;

        StylingRecommendationResponse response = stylingService.createRecommendation(memberId, targetProductId);

        return ApiResponse.success(StylingSuccessCode.CREATED, response);
    }

    @Operation(summary = "스타일링 저장 API", description = "생성된 스타일링을 저장합니다.")
    @PostMapping("/stylings/{stylingId}/save")
    public ApiResponse<StylingSaveResponse> saveStyling(
            @PathVariable Long stylingId,
            Long memberId
    ) {

        memberId = (memberId == null) ? 1L : memberId;

        StylingSaveResponse response = stylingService.saveStyling(memberId, stylingId);

        return ApiResponse.success(StylingSuccessCode.OK, response);
    }

    @Operation(summary = "저장한 스타일링 목록 조회 API", description = "저장한 스타일링 목록을 저장합니다.")
    @GetMapping("/me/stylings")
    public ApiResponse<MyStylingListResponse> getMyStyling(
            Long memberId,
            @Parameter(description = "페이지 번호 (1부터 시작)")
            @RequestParam(defaultValue = "1") Integer page,

            @Parameter(description = "한 페이지에 보여줄 개수")
            @RequestParam(defaultValue = "10") Integer size
    ) {

        memberId = (memberId == null) ? 1L : memberId;

        MyStylingListResponse response = stylingService.getMyStyling(memberId, page, size);

        return ApiResponse.success(StylingSuccessCode.OK, response);
    }

    @Operation(summary = "저장한 스타일링 상제 조회 API", description = "저장한 스타일링에 대한 기록을 조회합니다.")
    @GetMapping("/me/stylings/{stylingId}")
    public ApiResponse<MyStylingDetailResponse> getMyStylingDetail(
            Long memberId,
            @PathVariable Long stylingId
    ) {

        memberId = (memberId == null) ? 1L : memberId;

        MyStylingDetailResponse response = stylingService.getMyStylingDetail(memberId, stylingId);

        return ApiResponse.success(StylingSuccessCode.OK, response);
    }
}
