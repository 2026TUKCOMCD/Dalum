package dalum.dalum.domain.like_product.repository;

import dalum.dalum.domain.like_product.entity.LikeProduct;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.product.entity.Product;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;
import java.util.Set;

public interface LikeProductRepository extends JpaRepository<LikeProduct, Long> {

    // 좋아요를 누른 상품들 전부 조회
    @Query("SELECT lp.product.id FROM LikeProduct lp " +
            "WHERE lp.member.id = :memberId AND lp.product.id IN :productIds")
    Set<Long> findLikeProductIds(@Param("memberId") Long memberId,
                                 @Param("productIds") List<Long> productIds);

    // 이미 좋아요를 눌렀는지 확인
    Optional<LikeProduct> findByMemberAndProduct(Member member, Product product);

    // 좋아요 여부만 빠르게 확인
    boolean existsByMemberAndProduct(Member member, Product product);

    Page<LikeProduct> findAllByMemberOrderByCreatedAtDesc(Member member, Pageable pageable);

    void deleteByMemberId(Long memberId);

}
