package dalum.dalum.domain.dupe_product.service;
 
import dalum.dalum.domain.dupe_product.dto.request.DupeSearchRequest;
import dalum.dalum.domain.dupe_product.dto.response.DupeSearchResponse;
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
import dalum.dalum.domain.product.repository.ProductRepository;
import dalum.dalum.domain.search_log.entity.SearchLog;
import dalum.dalum.domain.search_log.repository.SearchLogRepository;
import dalum.dalum.global.ai.AiService;
import dalum.dalum.global.s3.S3Service;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;
import java.io.IOException;
import java.util.List;
import java.util.Set;
 
@Service
@RequiredArgsConstructor
@Transactional
 
// AI, S3는 Mock 처리
 
public class DupeSearchService {
 
    private static final int DEFAULT_TOP_K = 10;
 
    private final DupeProductRepository dupeProductRepository;
    private final ProductRepository productRepository;
    private final LikeProductRepository likeProductRepository;
    private final SearchLogRepository searchLogRepository;
    private final MemberRepository memberRepository;
    private final ProductConverter productConverter;
    private final AiService aiService;
    private final S3Service s3Service;
 
    public DupeSearchResponse searchDupe(Long memberId, DupeSearchRequest request) throws IOException {
        Member member = memberRepository.findById(memberId)
                .orElseThrow(() -> new MemberException(MemberErrorCode.NOT_FOUND));
 
        // s3 사용시에 필요
        MultipartFile file = request.image();
 
         String imageUrl = s3Service.uploadFile(file);
 
        // searchLog 생성
        SearchLog searchLog = getLog(request, member, imageUrl);
        searchLogRepository.save(searchLog);
 
        // 듀프 제품 추천받기
        List<Long> recommendProductIds = aiService.getRecommendations(file, DEFAULT_TOP_K);
 
        List<Product> products = productRepository.findAllById(recommendProductIds);
 
        // 듀프 제품 저장
        saveDupeProducts(products, searchLog);
 
        // 좋아요 눌렀는지 확인하기
        Set<Long> likeProductIds = likeProductRepository.findLikeProductIds(memberId, recommendProductIds);
 
        List<ProductDto> productDtos = productConverter.toProductDtoList(products, likeProductIds);
 
        return DupeSearchResponse.of(searchLog.getId(), productDtos);
 
    }
 
    private static SearchLog getLog(DupeSearchRequest request, Member member, String imageUrl) {
        SearchLog searchLog = SearchLog.builder()
                .member(member)
                .inputImageUrl(imageUrl)
                .brand(request.brand())
                .minPrice(request.minPrice())
                .maxPrice(request.maxPrice())
                .build();
        return searchLog;
    }
 
    private void saveDupeProducts(List<Product> products, SearchLog searchLog) {
        int rank = 1;
        for (Product product : products) {
            DupeProduct dupeProduct = DupeProduct.builder()
                    .searchLog(searchLog)
                    .product(product)
                    .rank(rank++)
                    .similarityScore(80.0)
                    .build();
            dupeProductRepository.save(dupeProduct);
        }
    }
 
 
 
 
}