package dalum.dalum.domain.dupe_product.dto.request;

import org.springframework.web.multipart.MultipartFile;

public record DupeSearchRequest(
//        MultipartFile image,
        String image,
        String brand,
        Integer minPrice,
        Integer maxPrice

) {
}
