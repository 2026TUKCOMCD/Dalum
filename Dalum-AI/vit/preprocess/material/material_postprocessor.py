from vit.preprocess.material.fiber_policy import ALL_CATEGORY_ALLOWED_FIBERS


class MaterialPostProcessor:

    def __init__(self, confidence_threshold=0.20, margin_threshold=0.03):
        """
        confidence_threshold : 최소 신뢰도 기준 (Soft 적용)
        margin_threshold     : top1 - top2 차이 최소 기준
        """
        self.confidence_threshold = confidence_threshold
        self.margin_threshold = margin_threshold

    def select_material(self, top3_list, full_prob_dict, category):

        if not top3_list:
            return "UNKNOWN"

        # 카테고리 기반 필터
        allowed = ALL_CATEGORY_ALLOWED_FIBERS.get(category)

        if allowed:
            # 전체 확률 중 허용 섬유만 추출
            allowed_probs = {
                mat: full_prob_dict.get(mat, 0.0)
                for mat in allowed
            }

            # 확률 기준 정렬
            sorted_allowed = sorted(
                allowed_probs.items(),
                key=lambda x: x[1],
                reverse=True
            )

            best_mat, best_prob = sorted_allowed[0]

        else:
            # 정책 없으면 top1 사용
            best_mat, best_prob = top3_list[0]

        # margin 체크
        if len(top3_list) > 1:
            top1_prob = top3_list[0][1]
            top2_prob = top3_list[1][1]
            margin = top1_prob - top2_prob

            if margin < self.margin_threshold:
                # 너무 애매하면 그냥 허용 섬유 최고값 반환
                return best_mat
            
        # confidence soft 적용
        if best_prob < self.confidence_threshold:
            return best_mat

        return best_mat
