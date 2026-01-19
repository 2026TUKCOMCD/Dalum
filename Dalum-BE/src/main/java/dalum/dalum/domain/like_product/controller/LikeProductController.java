package dalum.dalum.domain.like_product.controller;

import dalum.dalum.domain.like_product.dto.response.LikeToggleResponse;
import dalum.dalum.domain.like_product.service.LikeProductService;
import dalum.dalum.domain.product.exception.code.ProductSuccessCode;
import dalum.dalum.global.apipayload.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1")
public class LikeProductController {

    private final LikeProductService likeProductService;

    @Operation(summary = "상품 좋아요 토글", description = "상품 ID를 받아와 좋아요를 등록하거나 취소합니다.")
    @PostMapping("/products/{productId}/likes")
    public ApiResponse<LikeToggleResponse> toggleLike(
            @PathVariable Long productId,
            Long memberId // @AuthenticationPrincipal
    ) {

        memberId = (memberId == null) ? 1L : memberId; // 임시

        LikeToggleResponse response = likeProductService.toggleLike(productId, memberId);

        return ApiResponse.success(ProductSuccessCode.OK, response);
    }
}
