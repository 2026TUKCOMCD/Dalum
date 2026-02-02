package dalum.dalum.global.apipayload;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import dalum.dalum.global.apipayload.code.BaseErrorCode;
import dalum.dalum.global.apipayload.code.BaseSuccessCode;
import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
@JsonPropertyOrder({"isSuccess", "code", "message", "result"})
public class ApiResult<T> {

    @JsonProperty("isSuccess")
    private final Boolean isSuccess;

    @JsonProperty("code")
    private final String code;

    @JsonProperty("message")
    private final String message;

    @JsonProperty("result")
    private T result;

    public static <T> ApiResult<T> success(BaseSuccessCode code, T result) {
        return new ApiResult<>(true, code.getCode(), code.getMessage(), result);
    }

    public static <T> ApiResult<T> onFailure(BaseErrorCode code, T result) {
        return new ApiResult<>(false, code.getCode(), code.getMessage(), result);
    }
}
