package dalum.dalum.domain.styling.service;

import dalum.dalum.domain.like_product.entity.LikeProduct;
import dalum.dalum.domain.like_product.exception.LikeProductException;
import dalum.dalum.domain.like_product.exception.code.LikeProductErrorCode;
import dalum.dalum.domain.like_product.repository.LikeProductRepository;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.exception.MemberException;
import dalum.dalum.domain.member.exception.code.MemberErrorCode;
import dalum.dalum.domain.member.repository.MemberRepository;
import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.product.enums.LargeCategory;
import dalum.dalum.domain.product.exception.ProductException;
import dalum.dalum.domain.product.exception.code.ProductErrorCode;
import dalum.dalum.domain.product.repository.ProductRepository;
import dalum.dalum.domain.product.repository.projection.ProductCandidateProjection;
import dalum.dalum.domain.styling.client.AiStylingClient;
import dalum.dalum.domain.styling.client.dto.AiCandidateItem;
import dalum.dalum.domain.styling.client.dto.AiInputItem;
import dalum.dalum.domain.styling.client.dto.AiRecommendRequest;
import dalum.dalum.domain.styling.client.dto.AiRecommendedItem;
import dalum.dalum.domain.styling.converter.StylingConverter;
import dalum.dalum.domain.styling.dto.response.MyStylingDetailResponse;
import dalum.dalum.domain.styling.dto.response.MyStylingListResponse;
import dalum.dalum.domain.styling.dto.response.RecommendationCategoryResponse;
import dalum.dalum.domain.styling.dto.response.StylingSaveResponse;
import dalum.dalum.domain.styling.dto.response.StylingRecommendationResponse;
import dalum.dalum.domain.styling.entity.Styling;
import dalum.dalum.domain.styling.exception.StylingException;
import dalum.dalum.domain.styling.exception.code.StylingErrorCode;
import dalum.dalum.domain.styling.repository.StylingRepository;
import dalum.dalum.domain.styling_product.entity.StylingProduct;
import dalum.dalum.domain.styling_product.repository.StylingProductRepository;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class StylingServiceImpl implements StylingService {

    private static final Logger logger = LoggerFactory.getLogger(StylingServiceImpl.class);

    private static final double SCORE_THRESHOLD = 0.1;
    private static final double STYLE_FILTER_THRESHOLD = 0.5;

    private static final Map<LargeCategory, List<LargeCategory>> CATEGORY_MAP = new EnumMap<>(LargeCategory.class);

    static {
        CATEGORY_MAP.put(LargeCategory.BAG, List.of(LargeCategory.HAT, LargeCategory.OUTER, LargeCategory.TOP, LargeCategory.BOTTOM, LargeCategory.SHOES));
        CATEGORY_MAP.put(LargeCategory.TOP, List.of(LargeCategory.HAT, LargeCategory.OUTER, LargeCategory.BOTTOM, LargeCategory.SHOES, LargeCategory.BAG));
        CATEGORY_MAP.put(LargeCategory.BOTTOM, List.of(LargeCategory.HAT, LargeCategory.OUTER, LargeCategory.TOP, LargeCategory.SHOES, LargeCategory.BAG));
        CATEGORY_MAP.put(LargeCategory.OUTER, List.of(LargeCategory.HAT, LargeCategory.TOP, LargeCategory.BOTTOM, LargeCategory.SHOES, LargeCategory.BAG));
        CATEGORY_MAP.put(LargeCategory.DRESS, List.of(LargeCategory.HAT, LargeCategory.SHOES, LargeCategory.BAG));
        CATEGORY_MAP.put(LargeCategory.SHOES, List.of(LargeCategory.HAT, LargeCategory.OUTER, LargeCategory.TOP, LargeCategory.BOTTOM, LargeCategory.BAG));
        CATEGORY_MAP.put(LargeCategory.HAT, List.of(LargeCategory.OUTER, LargeCategory.TOP, LargeCategory.BOTTOM, LargeCategory.SHOES, LargeCategory.BAG));
    }

    private static final Map<String, Map<String, Double>> STYLE_COMPATIBILITY = Map.of(
            "casual",          Map.of("casual", 1.0, "american_casual", 0.9, "street", 0.7, "vintage", 0.6, "sporty", 0.5, "formal", 0.2),
            "formal",          Map.of("formal", 1.0, "casual", 0.3, "american_casual", 0.3, "street", 0.1, "vintage", 0.2, "sporty", 0.1),
            "sporty",          Map.of("sporty", 1.0, "casual", 0.7, "street", 0.5, "american_casual", 0.5, "vintage", 0.3, "formal", 0.1),
            "street",          Map.of("street", 1.0, "vintage", 0.8, "sporty", 0.7, "casual", 0.7, "american_casual", 0.2, "formal", 0.1),
            "vintage",         Map.of("vintage", 1.0, "street", 0.8, "american_casual", 0.7, "casual", 0.6, "sporty", 0.3, "formal", 0.3),
            "american_casual", Map.of("american_casual", 1.0, "casual", 0.8, "vintage", 0.7, "sporty", 0.5, "street", 0.2, "formal", 0.1)
    );

    private static List<String> getCompatibleStyles(String inputStyle) {
        if (inputStyle == null) return List.of("casual", "formal", "sporty", "street", "vintage", "american_casual");
        return STYLE_COMPATIBILITY.getOrDefault(inputStyle.toLowerCase(), Map.of())
                .entrySet().stream()
                .filter(e -> e.getValue() >= STYLE_FILTER_THRESHOLD)
                .map(Map.Entry::getKey)
                .toList();
    }

    private final MemberRepository memberRepository;
    private final ProductRepository productRepository;
    private final LikeProductRepository likeProductRepository;
    private final StylingRepository stylingRepository;
    private final StylingProductRepository stylingProductRepository;
    private final AiStylingClient aiStylingClient;

    private final StylingConverter stylingConverter;

    @Override
    public StylingRecommendationResponse createRecommendation(Long memberId, Long targetProductId) {

        Runtime rt = Runtime.getRuntime();
        long memBefore = rt.totalMemory() - rt.freeMemory();
        logger.info("[스타일링] 추천 시작 - 사용 메모리: {}MB", memBefore / 1024 / 1024);

        Member member = getMember(memberId);

        Product targetProduct = productRepository.findById(targetProductId).orElseThrow(
                () -> new ProductException(ProductErrorCode.NOT_FOUND));

        LikeProduct likeProduct = likeProductRepository.findByMemberAndProduct(member, targetProduct)
                .orElseThrow(() -> new LikeProductException(LikeProductErrorCode.NOT_FOUND));

        // AI 입력 구성
        String inputCategory = toCategoryString(targetProduct.getLargeCategory());
        AiInputItem aiInput = new AiInputItem(
                targetProduct.getMaterialVector() != null ? targetProduct.getMaterialVector() : List.of(),
                targetProduct.getDominantColors(),
                targetProduct.getStyle(),
                inputCategory
        );

        // 카테고리에 맞는 후보 상품 조회
        List<LargeCategory> candidateCategories = CATEGORY_MAP.getOrDefault(
                targetProduct.getLargeCategory(), List.of());
        List<String> compatibleStyles = getCompatibleStyles(targetProduct.getStyle());

        List<ProductCandidateProjection> candidates = candidateCategories.stream()
                .flatMap(cat -> productRepository.findCandidates(
                        List.of(cat), targetProductId, compatibleStyles, PageRequest.of(0, 500)).stream())
                .toList();

        long memAfterQuery = rt.totalMemory() - rt.freeMemory();
        logger.info("[스타일링] 후보 조회 완료 - 후보 수: {}개, 사용 메모리: {}MB (증가: {}MB)",
                candidates.size(), memAfterQuery / 1024 / 1024, (memAfterQuery - memBefore) / 1024 / 1024);

        // 후보 상품 → AI 요청 형태 변환
        List<AiCandidateItem> candidateItems = candidates.stream()
                .map(p -> new AiCandidateItem(
                        p.getId(),
                        toCategoryString(p.getLargeCategory()),
                        p.getStyle(),
                        p.getMaterialVector() != null ? p.getMaterialVector() : List.of(),
                        p.getDominantColors()))
                .toList();

        // AI 서버 호출
        AiRecommendRequest aiRequest = new AiRecommendRequest(aiInput, candidateItems, 3, SCORE_THRESHOLD);
        Map<String, List<AiRecommendedItem>> aiResponse = aiStylingClient.recommend(aiRequest);

        // 스타일링 저장
        Styling styling = Styling.builder()
                .member(member)
                .likeProduct(likeProduct)
                .build();
        stylingRepository.save(styling);

        // AI 결과에서 추천 상품 ID 수집
        List<Long> recommendedIds = aiResponse.values().stream()
                .flatMap(List::stream)
                .map(AiRecommendedItem::productId)
                .distinct()
                .toList();

        // 추천 상품 조회 및 StylingProduct 저장
        Map<Long, Product> productMap = productRepository.findAllById(recommendedIds).stream()
                .collect(Collectors.toMap(Product::getId, p -> p));

        List<StylingProduct> stylingProducts = recommendedIds.stream()
                .filter(productMap::containsKey)
                .map(id -> StylingProduct.builder()
                        .styling(styling)
                        .product(productMap.get(id))
                        .build())
                .toList();
        stylingProductRepository.saveAll(stylingProducts);

        // 좋아요 여부 확인
        List<Long> allProductIds = new ArrayList<>(recommendedIds);
        allProductIds.add(targetProductId);
        Set<Long> likedIds = likeProductRepository.findLikeProductIds(memberId, allProductIds);

        // 메인 상품 DTO 변환
        MyStylingDetailResponse.MainProductDetail mainProductDetail =
                stylingConverter.toMainProductDetailResponse(targetProduct, likedIds.contains(targetProductId));

        // 카테고리별 추천 상품 DTO 변환
        List<RecommendationCategoryResponse> resultItems = aiResponse.entrySet().stream()
                .filter(e -> !e.getValue().isEmpty())
                .map(e -> {
                    List<MyStylingDetailResponse.RecommendedItemDetail> dtos = e.getValue().stream()
                            .filter(item -> productMap.containsKey(item.productId()))
                            .map(item -> stylingConverter.toRecommendItemDetailResponse(
                                    productMap.get(item.productId()),
                                    likedIds.contains(item.productId())))
                            .toList();
                    return RecommendationCategoryResponse.builder()
                            .category(e.getKey())
                            .products(dtos)
                            .build();
                })
                .toList();

        long memAfter = rt.totalMemory() - rt.freeMemory();
        logger.info("[스타일링] 추천 완료 - 사용 메모리: {}MB (총 증가: {}MB)",
                memAfter / 1024 / 1024, (memAfter - memBefore) / 1024 / 1024);

        return StylingRecommendationResponse.builder()
                .stylingId(styling.getId())
                .mainItem(mainProductDetail)
                .resultItems(resultItems)
                .createdAt(styling.getCreatedAt())
                .build();
    }

    @Override
    public StylingSaveResponse saveStyling(Long memberId, Long stylingId) {
        getMember(memberId);
        Styling styling = stylingRepository.findById(stylingId).orElseThrow(
                () -> new StylingException(StylingErrorCode.NOT_FOUND));

        if (!styling.getMember().getId().equals(memberId)) {
            throw new StylingException(StylingErrorCode.FORBIDDEN); // 소유권 검증
        }

        styling.confirmSave();

        return stylingConverter.toStylingSaveResponse(styling.getId());
    }

    @Override
    @Transactional(readOnly = true)
    public MyStylingListResponse getMyStyling(Long memberId, Integer page, Integer size) {

        Member member = getMember(memberId);

        int pageIndex = (page != null && page > 0) ? page - 1 : 0;
        int pageSize = (size != null) ? size : 10;
        PageRequest pageRequest = PageRequest.of(pageIndex, pageSize);

        Page<Styling> stylingPage = stylingRepository.
                findAllByMemberIdAndIsScrappedTrueOrderByCreatedAtDesc(member.getId(), pageRequest);

        return stylingConverter.toMyStylingListResponse(stylingPage);
    }

    @Override
    public MyStylingDetailResponse getMyStylingDetail(Long memberId, Long stylingId) {

        Member member = getMember(memberId);

        Styling styling = stylingRepository.findById(stylingId).orElseThrow(
                () -> new StylingException(StylingErrorCode.NOT_FOUND));

        if (!styling.getMember().getId().equals(memberId)) {
            throw new StylingException(StylingErrorCode.FORBIDDEN);
        }

        if (styling.getLikeProduct() == null) {
            throw new LikeProductException(LikeProductErrorCode.NOT_FOUND);
        }

        Product mainProduct = styling.getLikeProduct().getProduct();

        List<StylingProduct> stylingProducts = stylingProductRepository.findByStyling(styling);

        List<Product> recommendedProducts = stylingProducts.stream()
                .map(StylingProduct::getProduct)
                .filter(p -> !p.getId().equals(mainProduct.getId()))
                .toList();

        Set<Long> allProductIds = new HashSet<>();
        allProductIds.add(mainProduct.getId());
        recommendedProducts.forEach(p -> allProductIds.add(p.getId()));

        Set<Long> likedIds = likeProductRepository.findLikeProductIds(member.getId(), new ArrayList<>(allProductIds));

        List<MyStylingDetailResponse.RecommendedItemDetail> itemDetails = recommendedProducts.stream()
                .map(p -> stylingConverter.toRecommendItemDetailResponse(p, likedIds.contains(p.getId())))
                .toList();

        return stylingConverter.toMyStylingDetailResponse(
                styling, mainProduct, likedIds.contains(mainProduct.getId()), itemDetails);
    }

    @Override
    public void deleteStyling(Long memberId, Long stylingId) {
        Styling styling = stylingRepository.findById(stylingId).orElseThrow(
                () -> new StylingException(StylingErrorCode.NOT_FOUND));

        if (!styling.getMember().getId().equals(memberId)) {
            throw new StylingException(StylingErrorCode.FORBIDDEN);
        }

        stylingRepository.delete(styling);
    }

    private Member getMember(Long memberId) {
        return memberRepository.findById(memberId).orElseThrow(
                () -> new MemberException(MemberErrorCode.NOT_FOUND));
    }

    private static String toCategoryString(LargeCategory category) {
        return switch (category) {
            case TOP -> "top";
            case BOTTOM -> "bottom";
            case SHOES -> "shoes";
            case OUTER -> "outer";
            case BAG -> "bag";
            case HAT -> "hat";
            case DRESS -> "dress";
        };
    }
}