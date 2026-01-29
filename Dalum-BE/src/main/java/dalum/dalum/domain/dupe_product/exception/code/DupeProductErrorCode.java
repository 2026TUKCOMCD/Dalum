package dalum.dalum.domain.dupe_product.exception.code;

import dalum.dalum.global.apipayload.code.BaseErrorCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum DupeProductErrorCode implements BaseErrorCode {
        NOT_FOUND(HttpStatus.NOT_FOUND,
                "DUPE_PRODUCT_404_1",
                "듀프 제품을 찾지 못했습니다.")
    ;
        private final HttpStatus status;
        private final String code;
        private final String message;

}
