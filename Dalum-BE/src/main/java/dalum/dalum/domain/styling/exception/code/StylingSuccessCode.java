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
            "스타일링을 성공적으로 조회하였습니다."),
    CREATED(HttpStatus.CREATED,
            "STYLING201_1",
            "스타일링이 성공적으로 생성되었습니다.")
    ;

    private final HttpStatus status;
    private final String code;
    private final String message;


}
