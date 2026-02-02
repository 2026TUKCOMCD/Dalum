package dalum.dalum.domain.dupe_product.dto.request;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import org.springframework.web.multipart.MultipartFile;


public record DupeSearchRequest(

        @Schema(description = "이미지 파일", type = "string", format = "binary", requiredMode = Schema.RequiredMode.REQUIRED)
        @NotNull(message = "이미지를 반드시 첨부해야 합니다.")
        MultipartFile image,

        @Schema(description = "브랜드명", example = "Nike")
        String brand,

        @Schema(description = "최소 가격", example = "10000")
        @Min(value = 10000, message = "최소 가격은 10000원 이상이어야 합니다.")
        Integer minPrice,

        @Schema(description = "최대 가격", example = "50000")
        @Max(value = 2000000, message = "최대 가격은 2000000원 이하이어야 합니다.")
        Integer maxPrice

) {
}
