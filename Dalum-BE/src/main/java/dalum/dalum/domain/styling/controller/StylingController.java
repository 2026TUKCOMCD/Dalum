package dalum.dalum.domain.styling.controller;

import dalum.dalum.domain.styling.dto.response.StylingRecommendationResponse;
import dalum.dalum.domain.styling.dto.response.StylingSaveResponse;
import dalum.dalum.domain.styling.exception.code.StylingSuccessCode;
import dalum.dalum.domain.styling.service.StylingService;
import dalum.dalum.domain.styling.service.StylingServiceImpl;
import dalum.dalum.global.apipayload.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

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
}
