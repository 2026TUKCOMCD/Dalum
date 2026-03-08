package dalum.dalum.global;

import lombok.Getter;
import java.util.List;

@Getter
public class AiDupeResponse {

    private List<Result> results;

    @Getter
    public static class Result {
        private Long productId;
    }
}