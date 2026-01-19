package dalum.dalum.domain.product.exception.code;

import dalum.dalum.global.apipayload.code.BaseSuccessCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum ProductSuccessCode implements BaseSuccessCode {
    OK(HttpStatus.OK,
            "PRODUCT200_1",
            "요청 성공")
    ;
    private final HttpStatus status;
    private final String code;
    private final String message;

}
