package dalum.dalum.domain.styling.exception.code;

import dalum.dalum.global.apipayload.code.BaseSuccessCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum StylingSuccessCode implements BaseSuccessCode {
    OK(HttpStatus.OK,
            "STYLING200_1",
            "요청 성공")
    ;
    private final HttpStatus status;
    private final String code;
    private final String message;


}
