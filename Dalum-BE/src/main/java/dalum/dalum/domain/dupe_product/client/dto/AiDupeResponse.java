package dalum.dalum.domain.dupe_product.client.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;

import java.util.List;

@Getter
public class AiDupeResponse {

    private String resultType;
    private int code;
    private String message;
    private Data data;

    @Getter
    public static class Data {
        private List<Result> results;
    }

    @Getter
    public static class Result {
        @JsonProperty("product_id")
        private Long productId;

        @JsonProperty("final_score")
        private Double finalScore;
    }
}
