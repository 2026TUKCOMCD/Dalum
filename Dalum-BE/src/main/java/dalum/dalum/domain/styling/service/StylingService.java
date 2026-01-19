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
import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.product.exception.ProductException;
import dalum.dalum.domain.product.exception.code.ProductErrorCode;
import dalum.dalum.domain.product.repository.ProductRepository;
import dalum.dalum.domain.styling.dto.response.StylingRecommendationResponse;
import dalum.dalum.domain.styling.entity.Styling;
import dalum.dalum.domain.styling.repository.StylingRepository;
import dalum.dalum.domain.styling_product.entity.StylingProduct;
import dalum.dalum.domain.styling_product.repository.StylingProductRepository;
import dalum.dalum.global.apipayload.exception.GeneralException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;

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

        List<Product> recommendedProducts = productRepository.findAllById(aiResultIds);

        List<Product> allItems = new ArrayList<>();
        allItems.add(targetProduct);
        allItems.addAll(recommendedProducts);



    }

    private static Styling getStyling(Member member, LikeProduct likeProduct) {
        Styling styling = Styling.builder()
                .member(member)
                .likeProduct(likeProduct)
                .build();
        return styling;
    }


}
