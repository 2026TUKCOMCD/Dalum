package dalum.dalum.domain.like_product.controller;

import dalum.dalum.domain.like_product.dto.response.LikeProductListResponse;
import dalum.dalum.domain.like_product.dto.response.LikeToggleResponse;
import dalum.dalum.domain.like_product.exception.code.LikeProductSuccessCode;
import dalum.dalum.domain.like_product.service.LikeProductService;
import dalum.dalum.domain.product.exception.code.ProductSuccessCode;
import dalum.dalum.global.apipayload.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import lombok.RequiredArgsConstructor;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1")
public class LikeProductController {

    private final LikeProductService likeProductService;

    @Operation(summary = "상품 좋아요/취소 토글 ", description = "상품 ID를 받아와 좋아요를 등록하거나 취소합니다.")
    @PostMapping("/products/{productId}/likes")
    public ApiResponse<LikeToggleResponse> toggleLike(
            @PathVariable Long productId,
            Long memberId // @AuthenticationPrincipal
    ) {

        memberId = (memberId == null) ? 1L : memberId; // 임시

        LikeToggleResponse response = likeProductService.toggleLike(productId, memberId);

        return ApiResponse.success(ProductSuccessCode.OK, response);
    }

    @Operation(summary = "좋아요한 상품 조회 API", description = "좋아요한 상품을 조회합니다.")
    @GetMapping("/me/likes")
    public ApiResponse<LikeProductListResponse> getLikeProducts(
            Long memberId,
            @Parameter(description = "페이지 번호 (1부터 시작)")
            @RequestParam(defaultValue = "1") Integer page,

            @Parameter(description = "한 페이지에 보여줄 개수")
            @RequestParam(defaultValue = "10") Integer size
    ) {

        memberId = (memberId == null) ? 1L : memberId;

        LikeProductListResponse response = likeProductService.getLikeProducts(memberId, page, size);

        return ApiResponse.success(LikeProductSuccessCode.OK, response);
    }
}
