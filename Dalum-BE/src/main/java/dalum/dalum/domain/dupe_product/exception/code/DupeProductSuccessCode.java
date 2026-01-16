package dalum.dalum.domain.dupe_product.exception.code;

import dalum.dalum.global.apipayload.code.BaseSuccessCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum DupeProductSuccessCode implements BaseSuccessCode {

    FOUND(HttpStatus.FOUND,
            "DUPEPRODUCT_200_1",
            "듀프제품을 성공적으로 조회했습니다.")
    ;
    private final HttpStatus status;
    private final String code;
    private final String message;

}
