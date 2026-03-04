package dalum.dalum.domain.like_product.exception.code;

import dalum.dalum.global.apipayload.code.BaseSuccessCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum LikeProductSuccessCode implements BaseSuccessCode {
    OK(HttpStatus.OK,
            "LIKE_PRODUCT_200_1",
            "좋아요한 상품을 성공적으로 조회했습니다.")
    ;
    private final HttpStatus status;
    private final String code;
    private final String message;
}
