package dalum.dalum.domain.dupe_product.service;

import dalum.dalum.domain.dupe_product.dto.request.DupeSearchRequest;
import dalum.dalum.domain.dupe_product.dto.response.DupeSearchResponse;
import dalum.dalum.domain.dupe_product.enitty.DupeProduct;
import dalum.dalum.domain.dupe_product.repository.DupeProductRepository;
import dalum.dalum.domain.like_product.repository.LikeProductRepository;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.exception.code.MemberErrorCode;
import dalum.dalum.domain.member.repository.MemberRepository;
import dalum.dalum.domain.product.converter.ProductConverter;
import dalum.dalum.domain.product.dto.response.ProductDto;
import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.product.repository.ProductRepository;
import dalum.dalum.domain.search_log.entity.SearchLog;
import dalum.dalum.domain.search_log.repository.SearchLogRepository;
import dalum.dalum.global.apipayload.exception.GeneralException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Set;

@Service
@RequiredArgsConstructor
@Transactional

// AI, S3는 Mock 처리

public class DupeSearchService {

    private final DupeProductRepository dupeProductRepository;
    private final ProductRepository productRepository;
    private final LikeProductRepository likeProductRepository;
    private final SearchLogRepository searchLogRepository;
    private final MemberRepository memberRepository;
    private final ProductConverter productConverter;

    public DupeSearchResponse searchDupe(Long memberId, DupeSearchRequest request) {
        Member member = memberRepository.findById(memberId)
                .orElseThrow(() -> new GeneralException(MemberErrorCode.NOT_FOUND));

        // s3 사용시에 필요
//        MultipartFile file = request.image();

        String imageUrl = "https://via.placeholder.com/500?text=MockImage";
        // String imageUrl = s3Service.upload(image); -> S3 코드로 변경해야함

        // searchLog 생성
        SearchLog searchLog = getLog(request, member);

        searchLogRepository.save(searchLog);

        // 듀프 제품 추천받기
        List<Long> recommendProductIds = List.of(1L, 2L, 3L);
        // List<Long> recommendProductIds = aiService.getRecommendations(imageUrl);

        List<Product> products = productRepository.findAllById(recommendProductIds);

        // 듀프 제품 저장
        saveDupeProducts(products, searchLog);

        // 좋아요 눌렀는지 확인하기
        Set<Long> likeProductIds = likeProductRepository.findLikeProductIds(memberId, recommendProductIds);

        List<ProductDto> productDtos = productConverter.toProductDtoList(products, likeProductIds);

        return DupeSearchResponse.of(searchLog.getId(), productDtos);

    }

    private static SearchLog getLog(DupeSearchRequest request, Member member) {
        SearchLog searchLog = SearchLog.builder()
                .member(member)
                .inputImageUrl(request.image())
                .brand(request.brand())
                .minPrice(request.minPrice())
                .maxPrice(request.maxPrice())
                .build();
        return searchLog;
    }

    private void saveDupeProducts(List<Product> products, SearchLog searchLog) {
        for (Product product : products) {
            DupeProduct dupeProduct = DupeProduct.builder()
                    .searchLog(searchLog)
                    .product(product)
                    .rank(1)
                    .similarityScore(80.0)
                    .build();
            dupeProductRepository.save(dupeProduct);
        }
    }




}

