package dalum.dalum.domain.auth.exception.code;

import dalum.dalum.global.apipayload.code.BaseSuccessCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum AuthSuccessCode implements BaseSuccessCode {
    OK(HttpStatus.OK,
            "AUTH_200_1",
            "로그인 성공입니다."),
    REISSUE(HttpStatus.OK,
            "AUTH_200_2",
            "토큰 재발급 성공입니다.");
    private final HttpStatus status;
    private final String code;
    private final String message;

}
