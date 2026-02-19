from vit.preprocess.face.face_judge import has_real_face

class Step1FaceJudge:
    def __init__(self, face_detector, face_index):
        self.face_detector = face_detector
        self.face_index = face_index

    def is_model_candidate(self, image) -> bool:
        is_face, _ = has_real_face(
            image=image,
            face_detector=self.face_detector,
            face_index=self.face_index,
            debug=False,
            apply_bbox_filter=True
        )
        return is_face