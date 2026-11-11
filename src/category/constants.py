# Константи (коди помилок, статуси)
import enum

class CategoryStatus(str, enum.Enum):
    ACTIVE = "1"
    INACTIVE = "0"

# Constraints for Category
MAX_CATEGORY_NAME_LENGTH = 255
MAX_SEO_KEYWORD_LENGTH = 255
MAX_META_TITLE_LENGTH = 255
MAX_META_KEYWORD_LENGTH = 255
MAX_IMAGE_PATH_LENGTH = 255
