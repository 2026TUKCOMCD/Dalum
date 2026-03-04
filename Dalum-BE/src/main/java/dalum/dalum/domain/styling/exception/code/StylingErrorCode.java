package dalum.dalum.domain.styling.exception.code;

import dalum.dalum.global.apipayload.code.BaseErrorCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum StylingErrorCode implements BaseErrorCode {
    NOT_FOUND(HttpStatus.NOT_FOUND,
            "STYLING_404_1",
            "해당 스타일링을 찾지 못했습니다."),
    ;
    private final HttpStatus status;
    private final String code;
    private final String message;
}

