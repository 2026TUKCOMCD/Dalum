package dalum.dalum.domain.like_product.exception.code;

import dalum.dalum.global.apipayload.code.BaseErrorCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum LikeProductErrorCode implements BaseErrorCode {
    NOT_FOUND(HttpStatus.NOT_FOUND,
            "LIKE_PRODUCT_404_1",
            "해당 좋아요 제품을 찾지 못했습니다."),
    ;
    private final HttpStatus status;
    private final String code;
    private final String message;

}
