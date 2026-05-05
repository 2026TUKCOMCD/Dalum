package dalum.dalum.domain.dupe_product.service;

import dalum.dalum.domain.dupe_product.dto.request.DupeSearchRequest;
import dalum.dalum.domain.dupe_product.dto.response.DupeProductDto;
import dalum.dalum.domain.dupe_product.dto.response.DupeSearchResponse;
import dalum.dalum.domain.dupe_product.enitty.DupeProduct;
import dalum.dalum.domain.dupe_product.repository.DupeProductRepository;
import dalum.dalum.domain.like_product.repository.LikeProductRepository;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.exception.MemberException;
import dalum.dalum.domain.member.exception.code.MemberErrorCode;
import dalum.dalum.domain.member.repository.MemberRepository;
import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.product.repository.ProductRepository;
import dalum.dalum.domain.search_log.entity.SearchLog;
import dalum.dalum.domain.search_log.repository.SearchLogRepository;
import dalum.dalum.global.ai.AiDupeResult;
import dalum.dalum.global.ai.AiService;
import dalum.dalum.global.s3.S3Service;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class DupeSearchService {

    private static final int DEFAULT_TOP_K = 10;

    private final DupeProductRepository dupeProductRepository;
    private final ProductRepository productRepository;
    private final LikeProductRepository likeProductRepository;
    private final SearchLogRepository searchLogRepository;
    private final MemberRepository memberRepository;
    private final AiService aiService;
    private final S3Service s3Service;

    public DupeSearchResponse searchDupe(Long memberId, DupeSearchRequest request) throws IOException {
        Member member = memberRepository.findById(memberId)
                .orElseThrow(() -> new MemberException(MemberErrorCode.NOT_FOUND));

        MultipartFile file = request.image();

        String s3Key = s3Service.uploadFile(file);
        String imageUrl = s3Service.getFileUrl(s3Key);

        SearchLog searchLog = SearchLog.builder()
                .member(member)
                .inputImageUrl(imageUrl)
                .brand(request.brand())
                .minPrice(request.minPrice())
                .maxPrice(request.maxPrice())
                .build();
        searchLogRepository.save(searchLog);

        List<AiDupeResult> aiResults = aiService.getRecommendations(s3Key, DEFAULT_TOP_K);

        List<Long> productIds = aiResults.stream().map(AiDupeResult::productId).toList();
        List<Product> products = productRepository.findAllById(productIds);
        Map<Long, Product> productMap = products.stream()
                .collect(Collectors.toMap(Product::getId, p -> p));

        saveDupeProducts(aiResults, productMap, searchLog);

        Set<Long> likeProductIds = likeProductRepository.findLikeProductIds(memberId, productIds);

        List<DupeProductDto> productDtos = aiResults.stream()
                .filter(r -> productMap.containsKey(r.productId()))
                .map(r -> {
                    Product product = productMap.get(r.productId());
                    return DupeProductDto.builder()
                            .productId(product.getId())
                            .name(product.getProductName())
                            .brand(product.getBrand())
                            .category(product.getLargeCategory().name())
                            .discountRate(product.getDiscountRate())
                            .price(product.getPrice())
                            .imageUrl(product.getImageUrl())
                            .purchaseUrl(product.getPurchaseLink())
                            .isLiked(likeProductIds.contains(product.getId()))
                            .colorScore(r.colorScore())
                            .materialScore(r.materialScore())
                            .designScore(r.designScore())
                            .totalScore(r.totalScore())
                            .build();
                })
                .toList();

        return DupeSearchResponse.of(searchLog.getId(), productDtos);
    }

    private void saveDupeProducts(List<AiDupeResult> aiResults, Map<Long, Product> productMap, SearchLog searchLog) {
        int rank = 1;
        for (AiDupeResult result : aiResults) {
            Product product = productMap.get(result.productId());
            if (product == null) continue;
            DupeProduct dupeProduct = DupeProduct.builder()
                    .searchLog(searchLog)
                    .product(product)
                    .rank(rank++)
                    .similarityScore(result.totalScore())
                    .colorScore(result.colorScore())
                    .materialScore(result.materialScore())
                    .designScore(result.designScore())
                    .build();
            dupeProductRepository.save(dupeProduct);
        }
    }
}