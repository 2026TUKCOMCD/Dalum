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
import dalum.dalum.domain.product.exception.ProductException;
import dalum.dalum.domain.product.exception.code.ProductErrorCode;
import dalum.dalum.domain.product.repository.ProductRepository;
import dalum.dalum.domain.styling.converter.StylingConverter;
import dalum.dalum.domain.styling.dto.response.MyStylingDetailResponse;
import dalum.dalum.domain.styling.dto.response.MyStylingListResponse;
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
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class StylingServiceImpl implements StylingService {

    private final MemberRepository memberRepository;
    private final ProductRepository productRepository;
    private final LikeProductRepository likeProductRepository;
    private final StylingRepository stylingRepository;
    private final StylingProductRepository stylingProductRepository;

    private final ProductConverter productConverter;
    private final StylingConverter stylingConverter;

    @Override
    public StylingRecommendationResponse createRecommendation(Long memberId, Long targetProductId) {

        Member member = getMember(memberId);

        Product targetProduct = productRepository.findById(targetProductId).orElseThrow(
                () -> new ProductException(ProductErrorCode.NOT_FOUND));

        LikeProduct likeProduct = likeProductRepository.findById(targetProductId).orElseThrow(
                () -> new LikeProductException(LikeProductErrorCode.NOT_FOUND));

        // AI 반환 결과 필요 -> 제품들이 리스트 형태로 반환
        List<Long> aiResultIds = new ArrayList<>();

        Styling styling = getStyling(member, likeProduct);
        stylingRepository.save(styling);

        // 추천받은 상품들 조회
        List<Product> recommendedProducts = productRepository.findAllById(aiResultIds);

        // 추천받은 상품들 저장
        List<Product> allProducts = new ArrayList<>();
        allProducts.add(targetProduct);
        allProducts.addAll(recommendedProducts);

        // 좋아요 여부 확인
        List<Long> allProductIds = allProducts.stream().map(Product::getId).collect(Collectors.toList());
        Set<Long> likeProductsIds = likeProductRepository.findLikeProductIds(memberId, allProductIds);

        // 메인 상품 변환
        ProductDto mainProductDto = productConverter.toProductDto(targetProduct, likeProductsIds.contains(targetProduct.getId()));

        // 추천 받은 상품들 리스트로 변환
        List<ProductDto> recommendProductsDtos = productConverter.toProductDtoList(recommendedProducts, likeProductsIds);

        StylingRecommendationResponse response = stylingConverter.toResponse(styling, mainProductDto, recommendProductsDtos);

        return response;

    }

    @Override
    public StylingSaveResponse saveStyling(Long memberId, Long stylingId) {
        Styling styling = stylingRepository.findById(stylingId).orElseThrow(
                () -> new StylingException(StylingErrorCode.NOT_FOUND));

        styling.confirmSave();

        StylingSaveResponse response = stylingConverter.toStylingSaveResponse(styling.getId());
        return response;

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

        MyStylingListResponse response = stylingConverter.toMyStylingListResponse(stylingPage);

        return response;

    }

    @Override
    public MyStylingDetailResponse getMyStylingDetail(Long memberId, Long stylingId) {

        Member member = getMember(memberId);

        Styling styling = stylingRepository.findById(stylingId).orElseThrow(
                () -> new StylingException(StylingErrorCode.NOT_FOUND));

        // 좋아요한 상품이 존재하지 않을 경우 예외 처리
        if (styling.getLikeProduct() == null) {
            throw new LikeProductException(LikeProductErrorCode.NOT_FOUND);
        }
        // 메인 상품 가져오기
        Product mainProduct = styling.getLikeProduct().getProduct();

        // 추천된 모든 상품 가져오기
        List<StylingProduct> stylingProducts = stylingProductRepository.findByStyling(styling);

        // 메인 상품 필터링
        List<Product> recommendedProducts = stylingProducts.stream()
                .map(StylingProduct::getProduct)
                .filter(p -> !p.getId().equals(mainProduct.getId()))
                .toList();

        // 좋아요 여부 계산 (메인 + 추천 상품 모두)
        Set<Long> allProductIds = new HashSet<>();
        allProductIds.add(mainProduct.getId());
        recommendedProducts.forEach(p -> allProductIds.add(p.getId()));

        Set<Long> likedIds = likeProductRepository.findLikeProductIds(member.getId(), new ArrayList<>(allProductIds));

        // 추천 아이템 DTO 변환
        List<MyStylingDetailResponse.RecommendedItemDetail> itemDetails = recommendedProducts.stream()
                .map(p -> stylingConverter.toRecommendItemDetailResponse(p, likedIds.contains(p.getId())))
                .toList();

        // 최종 DTO 변환
        MyStylingDetailResponse response = stylingConverter.toMyStylingDetailResponse(
                styling, mainProduct, likedIds.contains(mainProduct.getId()), itemDetails);

        return response;

    }

    private Member getMember(Long memberId) {
        return memberRepository.findById(memberId).orElseThrow(
                () -> new MemberException(MemberErrorCode.NOT_FOUND));
    }

    private static Styling getStyling(Member member, LikeProduct likeProduct) {
        Styling styling = Styling.builder()
                .member(member)
                .likeProduct(likeProduct)
                .build();
        return styling;
    }


}
