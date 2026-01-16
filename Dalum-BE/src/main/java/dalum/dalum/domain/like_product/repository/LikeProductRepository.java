package dalum.dalum.domain.like_product.repository;

import dalum.dalum.domain.like_product.entity.LikeProduct;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Set;

public interface LikeProductRepository extends JpaRepository<LikeProduct, Long> {

    // 좋아요를 누른 상품들 전부 조회
    @Query("SELECT lp.product.id FROM LikeProduct lp " +
            "WHERE lp.member.id = :memberId AND lp.product.id IN :productIds")
    Set<Long> findLikeProductIds(@Param("memberId") Long memberId,
                                 @Param("productIds") List<Long> productIds);
}
