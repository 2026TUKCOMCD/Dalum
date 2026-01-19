package dalum.dalum.domain.dupe_product.controller;

import dalum.dalum.domain.dupe_product.dto.request.DupeSearchRequest;
import dalum.dalum.domain.dupe_product.dto.response.DupeSearchResponse;
import dalum.dalum.domain.dupe_product.exception.code.DupeProductSuccessCode;
import dalum.dalum.domain.dupe_product.service.DupeSearchService;
import dalum.dalum.global.apipayload.ApiResponse;
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

    @Tag(name = "Search API", description = "듀프 제품 검색 API")
    @PostMapping(value = "/search/dupe", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ApiResponse<DupeSearchResponse> searchDupe(
            Long memberId,
            @ParameterObject @ModelAttribute DupeSearchRequest request
            ) {
        memberId = memberId == null ? 1L : memberId;

        DupeSearchResponse response = dupeSearchService.searchDupe(memberId, request);

        return ApiResponse.success(DupeProductSuccessCode.FOUND, response);

    }
}
