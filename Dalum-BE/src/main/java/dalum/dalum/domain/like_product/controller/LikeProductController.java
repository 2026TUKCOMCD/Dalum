package dalum.dalum.domain.like_product.controller;

import dalum.dalum.domain.like_product.dto.response.LikeProductListResponse;
import dalum.dalum.domain.like_product.dto.response.LikeToggleResponse;
import dalum.dalum.domain.like_product.exception.code.LikeProductSuccessCode;
import dalum.dalum.domain.like_product.service.LikeProductService;
import dalum.dalum.domain.product.exception.code.ProductSuccessCode;
import dalum.dalum.global.apipayload.ApiResult;
import dalum.dalum.global.security.SecurityUtil;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "Like Product", description = "좋아요 상품 관련 API")
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1")
public class LikeProductController {

    private final LikeProductService likeProductService;

    @Operation(summary = "상품 좋아요/취소 토글 ", description = "상품 ID를 받아와 좋아요를 등록하거나 취소합니다.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "PRODUCT_201_1", description = "상품 좋아요/취소가 성공적으로 처리되었습니다."),
            @ApiResponse(responseCode = "MEMBER_404_1", description = "해당 유저를 찾지 못했습니다."),
            @ApiResponse(responseCode = "PRODUCT_404_1", description = "해당 상품을 찾지 못했습니다."),
    })
    @PostMapping("/products/{productId}/likes")
    public ApiResult<LikeToggleResponse> toggleLike(
            @PathVariable Long productId
    ) {
        Long memberId = SecurityUtil.getCurrentMemberId();

        LikeToggleResponse response = likeProductService.toggleLike(memberId, productId);

        return ApiResult.success(ProductSuccessCode.LIKE_TOGGLE, response);
    }

    @Operation(summary = "좋아요한 상품 조회 API", description = "좋아요한 상품을 조회합니다.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "LIKE_PRODUCT_200_1", description = "좋아요한 상품을 성공적으로 조회하였습니다."),
            @ApiResponse(responseCode = "MEMBER_404_1", description = "해당 유저를 찾지 못했습니다."),
    })
    @GetMapping("/me/likes")
    public ApiResult<LikeProductListResponse> getLikeProducts(
            @Parameter(description = "페이지 번호 (1부터 시작)")
            @RequestParam(defaultValue = "1") Integer page,

            @Parameter(description = "한 페이지에 보여줄 개수")
            @RequestParam(defaultValue = "10") Integer size
    ) {

        Long memberId = SecurityUtil.getCurrentMemberId();

        LikeProductListResponse response = likeProductService.getLikeProducts(memberId, page, size);

        return ApiResult.success(LikeProductSuccessCode.OK, response);
    }
}
