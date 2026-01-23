package dalum.dalum.domain.dupe_product.controller;

import dalum.dalum.domain.dupe_product.dto.request.DupeSearchRequest;
import dalum.dalum.domain.dupe_product.dto.response.DupeSearchResponse;
import dalum.dalum.domain.dupe_product.exception.code.DupeProductSuccessCode;
import dalum.dalum.domain.dupe_product.service.DupeSearchService;
import dalum.dalum.global.apipayload.ApiResponse;
import dalum.dalum.global.security.SecurityUtil;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springdoc.core.annotations.ParameterObject;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1")
public class DupeProductController {

    private final DupeSearchService dupeSearchService;

    @Operation(summary= "듀프 제품 검색 API", description = "사진에 따른 듀프 제품을 검색합니다.")
    @PostMapping(value = "/search/dupe", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ApiResponse<DupeSearchResponse> searchDupe(
            @ParameterObject @ModelAttribute DupeSearchRequest request) {

        Long memberId = SecurityUtil.getCurrentMemberId();

        DupeSearchResponse response = dupeSearchService.searchDupe(memberId, request);

        return ApiResponse.success(DupeProductSuccessCode.FOUND, response);

    }
}
