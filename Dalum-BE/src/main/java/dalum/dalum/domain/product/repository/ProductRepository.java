package dalum.dalum.domain.product.repository;

import dalum.dalum.domain.like_product.entity.LikeProduct;
import dalum.dalum.domain.member.entity.Member;
import dalum.dalum.domain.product.entity.Product;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface ProductRepository extends JpaRepository<Product, Long> {


}
