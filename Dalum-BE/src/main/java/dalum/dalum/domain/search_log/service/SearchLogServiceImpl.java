package dalum.dalum.domain.search_log.service;

import dalum.dalum.domain.dupe_product.enitty.DupeProduct;
import dalum.dalum.domain.dupe_product.repository.DupeProductRepository;
import dalum.dalum.domain.like_product.repository.LikeProductRepository;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.exception.MemberException;
import dalum.dalum.domain.member.exception.code.MemberErrorCode;
import dalum.dalum.domain.member.repository.MemberRepository;
import dalum.dalum.domain.product.converter.ProductConverter;
import dalum.dalum.domain.product.dto.response.ProductDto;
import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.search_log.converter.SearchLogConverter;
import dalum.dalum.domain.search_log.dto.response.SearchLogDetailResponse;
import dalum.dalum.domain.search_log.dto.response.SearchLogListResponse;
import dalum.dalum.domain.search_log.entity.SearchLog;
import dalum.dalum.domain.search_log.exception.SearchLogException;
import dalum.dalum.domain.search_log.exception.code.SearchLogErrorCode;
import dalum.dalum.domain.search_log.repository.SearchLogRepository;
import dalum.dalum.global.apipayload.exception.GeneralException;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Set;

@Service
@RequiredArgsConstructor
@Transactional
public class SearchLogServiceImpl implements SearchLogService {

    private final SearchLogRepository searchLogRepository;
    private final MemberRepository memberRepository;
    private final DupeProductRepository dupeProductRepository;
    private final LikeProductRepository likeProductRepository;

    private final SearchLogConverter searchLogConverter;
    private final ProductConverter productConverter;

    public SearchLogListResponse getSearchLog(Long memberId, Integer page, Integer size) {
        Member member = memberRepository.findById(memberId).orElseThrow(
                () -> new MemberException(MemberErrorCode.NOT_FOUND));

        int pageIndex = (page != null && page > 0) ? page - 1 : 0; // 페이지는 0부터 시작
        int pageSize = (size != null) ? size : 10; // 기본값은 10

        PageRequest pageRequest = PageRequest.of(pageIndex, pageSize);

        Page<SearchLog> searchLogPage = searchLogRepository.findAllByMemberOrderByCreatedAt(member, pageRequest);

        SearchLogListResponse response = searchLogConverter.toSearchLogListResponse(searchLogPage);

        return response;
    }

    @Override
    public SearchLogDetailResponse getSearchLogDetail(Long memberId, Long searchLogId) {

        SearchLog searchLog = searchLogRepository.findById(searchLogId).orElseThrow(
                () -> new SearchLogException(SearchLogErrorCode.NOT_FOUND)
        );

        Member member = memberRepository.findById(memberId).orElseThrow(
                () -> new MemberException(MemberErrorCode.NOT_FOUND));

        // Dupe 테이블 조회
        List<DupeProduct> dupeProducts = dupeProductRepository.findBySearchLog(searchLog);

        // DupeProduct -> Product 객체 추출
        List<Product> products = dupeProducts.stream()
                .map(DupeProduct::getProduct)
                .toList();

        // 좋아요 여부 확인
        List<Long> productIds = products.stream().map(Product::getId).toList();
        Set<Long> likeProductIds = likeProductRepository.findLikeProductIds(member.getId(), productIds);

        // Product -> ProductDto로 변환
        List<ProductDto> productDtos = productConverter.toProductDtoList(products, likeProductIds);

        // 최종 응답 변환
        SearchLogDetailResponse response = searchLogConverter.toSearchLogDetailResponse(searchLog, productDtos);

        return response;
    }


}
