package dalum.dalum.domain.member.exception.code;

import dalum.dalum.global.apipayload.code.BaseSuccessCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum MemberSuccessCode implements BaseSuccessCode {
    OK(HttpStatus.OK,
            "MEMBER_200_1",
            "회원을 정상적으로 조회했습니다.")
    ;
    private final HttpStatus status;
    private final String code;
    private final String message;
}
