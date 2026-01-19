package dalum.dalum.domain.like_product.service;

import dalum.dalum.domain.like_product.dto.response.LikeToggleResponse;
import dalum.dalum.domain.like_product.entity.LikeProduct;
import dalum.dalum.domain.like_product.repository.LikeProductRepository;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.member.exception.MemberException;
import dalum.dalum.domain.member.exception.code.MemberErrorCode;
import dalum.dalum.domain.member.repository.MemberRepository;
import dalum.dalum.domain.product.entity.Product;
import dalum.dalum.domain.product.exception.ProductException;
import dalum.dalum.domain.product.exception.code.ProductErrorCode;
import dalum.dalum.domain.product.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional
public class LikeProductService {

    private final LikeProductRepository likeProductRepository;
    private final MemberRepository memberRepository;
    private final ProductRepository productRepository;

    public LikeToggleResponse toggleLike(Long memberId, Long productId) {

        Member member = memberRepository.findById(memberId).orElseThrow(
                () -> new MemberException(MemberErrorCode.NOT_FOUND));

        Product product = productRepository.findById(productId).orElseThrow(
                () -> new ProductException(ProductErrorCode.NOT_FOUND));

        // 좋아요 여부 검증
        boolean isLiked = getIsLiked(member, product);
        
        return new LikeToggleResponse(isLiked);
    }


    private Boolean getIsLiked(Member member, Product product) {
        // 좋아요가 등록되어 있다면 좋아요 취소
        return likeProductRepository.findByMemberAndProduct(member, product)
                .map(likeProduct -> {
                    likeProductRepository.delete(likeProduct);
                    return false;
                })
                // 좋아요가 되어 있지 않다면 좋아요 등록
                .orElseGet(() -> {
                    likeProductRepository.save(LikeProduct.builder()
                            .member(member)
                            .product(product)
                            .build());
                    return true;
                });
    }
}
