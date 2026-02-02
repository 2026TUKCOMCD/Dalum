package dalum.dalum.global.apipayload.exception;

import dalum.dalum.global.apipayload.ApiResult;
import dalum.dalum.global.apipayload.code.BaseErrorCode;
import dalum.dalum.global.apipayload.code.GeneralErrorCode;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GeneralExceptionAdvice {

    @ExceptionHandler(GeneralException.class)
    public ResponseEntity<ApiResult<Void>> handleException(
            GeneralException ex
    ) {

        return ResponseEntity.status(ex.getCode().getStatus())
                .body(ApiResult.onFailure(
                                ex.getCode(),
                                null
                        )
                );
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResult<String>> handleException(
            Exception ex
    ) {

        BaseErrorCode code = GeneralErrorCode.INTERNAL_SERVER_500;
        return ResponseEntity.status(code.getStatus())
                .body(ApiResult.onFailure(
                                code,
                                ex.getMessage()
                        )
                );
    }


}

