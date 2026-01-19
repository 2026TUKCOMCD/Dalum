package dalum.dalum.domain.product.exception;

import dalum.dalum.global.apipayload.code.BaseErrorCode;
import dalum.dalum.global.apipayload.exception.GeneralException;

public class ProductException extends GeneralException {
    public ProductException(BaseErrorCode code) {
        super(code);
    }
}
