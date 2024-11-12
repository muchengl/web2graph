from web_parser.omni_parser import initialize_models


class ModelManager:

    def __init__(self,
                 som_model_path='models/icon_detect/best.pt',
                 caption_model_name="blip2",
                 caption_model_path="models/icon_caption_blip2"):

        self.som_model_path = som_model_path
        self.caption_model_name = caption_model_name
        self.caption_model_path = caption_model_path

        self._som_model = None
        self._caption_model = None

    def get_som_model(self):
        if self._som_model is not None:
            return self._som_model

        self._som_model, self._caption_model = initialize_models(
            self.som_model_path,
            self.caption_model_name,
            self.caption_model_path
        )

        if self._som_model is not None:
            return self._som_model

        return None


    def get_caption_model(self):
        if self._caption_model is not None:
            return self._caption_model

        self._som_model, self._caption_model = initialize_models(
            self.som_model_path,
            self.caption_model_name,
            self.caption_model_path
        )

        if self._caption_model is not None:
            return self._caption_model

        return None
