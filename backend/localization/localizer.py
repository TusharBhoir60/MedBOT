"""
Localizer: Post-processes PatientResponse to translate string values
into the requested locale (en-IN, hi-IN, mr-IN) using exact or partial matches.
"""
import json
import logging
import os
from copy import deepcopy
from typing import Any, Dict, List

from schemas.patient_response import PatientResponse

logger = logging.getLogger(__name__)


class Localizer:
    """
    Translates string values in PatientResponse into the target language.
    Does NOT translate keys or internal schema fields.
    Falls back to en-IN for any missing translations.
    """

    def __init__(self, translations_dir: str = None) -> None:
        if not translations_dir:
            translations_dir = os.path.join(os.path.dirname(__file__), "translations")
        self.translations_dir = translations_dir
        self._cache: Dict[str, Dict[str, str]] = {}

    def _load_locale(self, locale: str) -> Dict[str, str]:
        if locale in self._cache:
            return self._cache[locale]

        path = os.path.join(self.translations_dir, f"{locale}.json")
        if not os.path.exists(path):
            logger.warning("Translations for locale '%s' not found. Falling back to en-IN.", locale)
            path = os.path.join(self.translations_dir, "en-IN.json")
            if not os.path.exists(path):
                self._cache[locale] = {}
                return {}

        with open(path, "r", encoding="utf-8") as f:
            self._cache[locale] = json.load(f)
        return self._cache[locale]

    def translate(self, response: PatientResponse, target_locale: str) -> PatientResponse:
        """
        Translates the patient response to the target locale.
        Returns a new translated PatientResponse object.
        """
        # If English requested or unsupported format, we just set the language field
        if target_locale.lower() == "en-in":
            resp_copy = response.model_copy(deep=True)
            resp_copy.language = "en-IN"
            return resp_copy

        dict_data = response.model_dump()
        translations = self._load_locale(target_locale)
        en_fallback = self._load_locale("en-IN")

        translated_dict = self._translate_node(dict_data, translations, en_fallback)
        translated_dict["language"] = target_locale

        return PatientResponse(**translated_dict)

    def _translate_node(
        self, node: Any, translations: Dict[str, str], fallback: Dict[str, str]
    ) -> Any:
        """Recursively translates string values in dictionaries and lists."""
        if isinstance(node, str):
            # Attempt exact match first
            if node in translations:
                return translations[node]
            # Case-insensitive match for single words
            lower_node = node.lower()
            if lower_node in translations:
                return translations[lower_node]

            # Very basic substring replacement (only safe for static templates)
            # In a real app this would use an LLM translation step for dynamic text.
            translated = node
            for key, val in translations.items():
                if key in translated and key != val:
                    translated = translated.replace(key, val)
            return translated

        if isinstance(node, dict):
            new_dict = {}
            for k, v in node.items():
                # We do not translate keys, only values
                new_dict[k] = self._translate_node(v, translations, fallback)
            return new_dict

        if isinstance(node, list):
            return [self._translate_node(item, translations, fallback) for item in node]

        return node
