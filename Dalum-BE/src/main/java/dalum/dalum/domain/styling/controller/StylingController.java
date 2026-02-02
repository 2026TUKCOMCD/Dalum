package dalum.dalum.domain.styling.controller;

import dalum.dalum.domain.styling.dto.response.MyStylingDetailResponse;
import dalum.dalum.domain.styling.dto.response.MyStylingListResponse;
import dalum.dalum.domain.styling.dto.response.StylingRecommendationResponse;
import dalum.dalum.domain.styling.dto.response.StylingSaveResponse;
import dalum.dalum.domain.styling.exception.code.StylingSuccessCode;
import dalum.dalum.domain.styling.service.StylingService;
import dalum.dalum.global.apipayload.ApiResult;
import dalum.dalum.global.security.SecurityUtil;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "Styling", description = "스타일링 관련 API")
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1")
public class StylingController {

    private final StylingService stylingService;

    @Operation(summary = "스타일링 추천 API", description = "AI가 좋아요한 제품에대해 스타일링을 생성합니다.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "STYLING_201_1", description = "스타일링 추천이 성공적으로 생성되었습니다."),
            @ApiResponse(responseCode = "MEMBER_404_1", description = "해당 유저를 찾지 못했습니다."),
            @ApiResponse(responseCode = "PRODUCT_404_1", description = "해당 상품을 찾지 못했습니다."),
            @ApiResponse(responseCode = "LIKE_PRODUCT_404_1", description = "좋아요한 상품을 찾지 못했습니다."),
    })
    @PostMapping("/stylings/recommend")
    public ApiResult<StylingRecommendationResponse> recommendProducts(Long targetProductId) {

        Long memberId = SecurityUtil.getCurrentMemberId();

        StylingRecommendationResponse response = stylingService.createRecommendation(memberId, targetProductId);

        return ApiResult.success(StylingSuccessCode.CREATED, response);
    }

    @Operation(summary = "스타일링 저장 API", description = "생성된 스타일링을 저장합니다.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "STYLING_200_1", description = "스타일링을 성공적으로 저장하였습니다."),
            @ApiResponse(responseCode = "STYLING_404_1", description = "해당 스타일링을 찾지 못했습니다."),
    })
    @PostMapping("/stylings/{stylingId}/save")
    public ApiResult<StylingSaveResponse> saveStyling(
            @PathVariable Long stylingId) {

        Long memberId = SecurityUtil.getCurrentMemberId();

        StylingSaveResponse response = stylingService.saveStyling(memberId, stylingId);

        return ApiResult.success(StylingSuccessCode.STORE, response);
    }

    @Operation(summary = "저장한 스타일링 목록 조회 API", description = "저장한 스타일링 목록을 저장합니다.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "STYLING_200_1", description = "저장한 스타일링을 성공적으로 조회하였습니다."),
            @ApiResponse(responseCode = "MEMBER_404_1", description = "해당 유저를 찾지 못했습니다."),
    })
    @GetMapping("/me/stylings")
    public ApiResult<MyStylingListResponse> getMyStyling(
            @Parameter(description = "페이지 번호 (1부터 시작)")
            @RequestParam(defaultValue = "1") Integer page,

            @Parameter(description = "한 페이지에 보여줄 개수")
            @RequestParam(defaultValue = "10") Integer size
    ) {

        Long memberId = SecurityUtil.getCurrentMemberId();

        MyStylingListResponse response = stylingService.getMyStyling(memberId, page, size);

        return ApiResult.success(StylingSuccessCode.OK, response);
    }

    @Operation(summary = "저장한 스타일링 상제 조회 API", description = "저장한 스타일링에 대한 기록을 조회합니다.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "STYLING_200_3", description = "스타일링 상세를 성공적으로 조회하였습니다."),
            @ApiResponse(responseCode = "MEMBER_404_1", description = "해당 유저를 찾지 못했습니다."),
            @ApiResponse(responseCode = "STYLING_404_2", description = "해당 스타일링 기록을 찾지 못했습니다."),
            @ApiResponse(responseCode = "LIKE_PRODUCT_404_1", description = "좋아요한 상품을 찾지 못했습니다."),
    })
    @GetMapping("/me/stylings/{stylingId}")
    public ApiResult<MyStylingDetailResponse> getMyStylingDetail(
            @PathVariable Long stylingId
    ) {

        Long memberId = SecurityUtil.getCurrentMemberId();

        MyStylingDetailResponse response = stylingService.getMyStylingDetail(memberId, stylingId);

        return ApiResult.success(StylingSuccessCode.DETAIL_OK, response);
    }
}
