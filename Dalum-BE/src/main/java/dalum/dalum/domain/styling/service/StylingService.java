package dalum.dalum.domain.styling.service;

import dalum.dalum.domain.like_product.entity.LikeProduct;
import dalum.dalum.domain.like_product.exception.LikeProductException;
import dalum.dalum.domain.like_product.exception.code.LikeProductError;
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
import dalum.dalum.domain.styling.dto.response.StylingRecommendationResponse;
import dalum.dalum.domain.styling.entity.Styling;
import dalum.dalum.domain.styling.repository.StylingRepository;
import dalum.dalum.domain.styling_product.repository.StylingProductRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class StylingService {

    private final MemberRepository memberRepository;
    private final ProductRepository productRepository;
    private final LikeProductRepository likeProductRepository;
    private final StylingRepository stylingRepository;
    private final StylingProductRepository stylingProductRepository;

    private final ProductConverter productConverter;
    private final StylingConverter stylingConverter;

    public StylingRecommendationResponse createRecommendation(Long memberId, Long targetProductId) {
        Member member = memberRepository.findById(memberId).orElseThrow(
                () -> new MemberException(MemberErrorCode.NOT_FOUND));

        Product targetProduct = productRepository.findById(targetProductId).orElseThrow(
                () -> new ProductException(ProductErrorCode.NOT_FOUND));

        LikeProduct likeProduct = likeProductRepository.findById(targetProductId).orElseThrow(
                () -> new LikeProductException(LikeProductError.NOT_FOUND));

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

    private static Styling getStyling(Member member, LikeProduct likeProduct) {
        Styling styling = Styling.builder()
                .member(member)
                .likeProduct(likeProduct)
                .build();
        return styling;
    }


}
