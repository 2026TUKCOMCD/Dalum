package dalum.dalum.domain.styling.service;

import dalum.dalum.domain.like_product.entity.LikeProduct;
import dalum.dalum.domain.like_product.exception.LikeProductException;
import dalum.dalum.domain.like_product.exception.code.LikeProductErrorCode;
import dalum.dalum.domain.like_product.repository.LikeProductRepository;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.exception.MemberException;
import dalum.dalum.domain.member.exception.code.MemberErrorCode;
import dalum.dalum.domain.member.repository.MemberRepository;
import dalum.dalum.domain.product.converter.ProductConverter;
import dalum.dalum.domain.product.dto.response.ProductDto;
import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.product.enums.LargeCategory;
import dalum.dalum.domain.product.exception.ProductException;
import dalum.dalum.domain.product.exception.code.ProductErrorCode;
import dalum.dalum.domain.product.repository.ProductRepository;
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

    private static final double SCORE_THRESHOLD = 0.1;

    private static final Map<LargeCategory, List<LargeCategory>> CATEGORY_MAP = new EnumMap<>(LargeCategory.class);

    static {
        CATEGORY_MAP.put(LargeCategory.TOP,    List.of(LargeCategory.BOTTOM, LargeCategory.SHOES, LargeCategory.BAG, LargeCategory.HAT));
        CATEGORY_MAP.put(LargeCategory.BOTTOM, List.of(LargeCategory.TOP, LargeCategory.SHOES, LargeCategory.BAG, LargeCategory.HAT));
        CATEGORY_MAP.put(LargeCategory.SHOES,  List.of(LargeCategory.TOP, LargeCategory.BOTTOM, LargeCategory.OUTER));
        CATEGORY_MAP.put(LargeCategory.OUTER,  List.of(LargeCategory.BOTTOM, LargeCategory.SHOES, LargeCategory.BAG));
        CATEGORY_MAP.put(LargeCategory.BAG,    List.of(LargeCategory.TOP, LargeCategory.BOTTOM, LargeCategory.OUTER, LargeCategory.SHOES));
        CATEGORY_MAP.put(LargeCategory.HAT,    List.of(LargeCategory.TOP, LargeCategory.BOTTOM, LargeCategory.OUTER));
        CATEGORY_MAP.put(LargeCategory.DRESS,  List.of(LargeCategory.SHOES, LargeCategory.BAG, LargeCategory.HAT));
    }

    private final MemberRepository memberRepository;
    private final ProductRepository productRepository;
    private final LikeProductRepository likeProductRepository;
    private final StylingRepository stylingRepository;
    private final StylingProductRepository stylingProductRepository;
    private final AiStylingClient aiStylingClient;

    private final ProductConverter productConverter;
    private final StylingConverter stylingConverter;

    @Override
    public StylingRecommendationResponse createRecommendation(Long memberId, Long targetProductId) {

        Member member = getMember(memberId);

        Product targetProduct = productRepository.findById(targetProductId).orElseThrow(
                () -> new ProductException(ProductErrorCode.NOT_FOUND));

        LikeProduct likeProduct = likeProductRepository.findByMemberAndProduct(member, targetProduct)
                .orElseThrow(() -> new LikeProductException(LikeProductErrorCode.NOT_FOUND));

        // AI 입력 구성
        String inputCategory = toCategoryString(targetProduct.getLargeCategory());
        AiInputItem aiInput = new AiInputItem(
                targetProduct.getMaterialVector() != null ? targetProduct.getMaterialVector() : Map.of(),
                targetProduct.getDominantColors(),
                targetProduct.getStyle(),
                inputCategory
        );

        // 카테고리에 맞는 후보 상품 조회
        List<LargeCategory> candidateCategories = CATEGORY_MAP.getOrDefault(
                targetProduct.getLargeCategory(), List.of());
        List<Product> candidates = productRepository.findCandidates(candidateCategories, targetProductId);

        // 후보 상품 → AI 요청 형태 변환
        List<AiCandidateItem> candidateItems = candidates.stream()
                .map(p -> new AiCandidateItem(
                        p.getId(),
                        toCategoryString(p.getLargeCategory()),
                        p.getStyle(),
                        p.getMaterialVector() != null ? p.getMaterialVector() : Map.of(),
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
        ProductDto mainProductDto = productConverter.toProductDto(targetProduct, likedIds.contains(targetProductId));

        // 카테고리별 추천 상품 DTO 변환
        List<RecommendationCategoryResponse> resultItems = aiResponse.entrySet().stream()
                .filter(e -> !e.getValue().isEmpty())
                .map(e -> {
                    List<ProductDto> dtos = e.getValue().stream()
                            .filter(item -> productMap.containsKey(item.productId()))
                            .map(item -> productConverter.toProductDto(
                                    productMap.get(item.productId()),
                                    likedIds.contains(item.productId())))
                            .toList();
                    return RecommendationCategoryResponse.builder()
                            .category(e.getKey())
                            .products(dtos)
                            .build();
                })
                .toList();

        return StylingRecommendationResponse.builder()
                .stylingId(styling.getId())
                .mainItem(mainProductDto)
                .resultItems(resultItems)
                .createdAt(styling.getCreatedAt())
                .build();
    }

    @Override
    public StylingSaveResponse saveStyling(Long memberId, Long stylingId) {
        Styling styling = stylingRepository.findById(stylingId).orElseThrow(
                () -> new StylingException(StylingErrorCode.NOT_FOUND));

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

    private Member getMember(Long memberId) {
        return memberRepository.findById(memberId).orElseThrow(
                () -> new MemberException(MemberErrorCode.NOT_FOUND));
    }

    private static String toCategoryString(LargeCategory category) {
        return switch (category) {
            case TOP    -> "top";
            case BOTTOM -> "bottom";
            case SHOES  -> "shoes";
            case OUTER  -> "outer";
            case BAG    -> "bag";
            case HAT    -> "accessory";
            case DRESS  -> "dress";
        };
    }
}