from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub

DIR_PATH = 'I18N/locales'


def i18n_factory() -> TranslatorHub:
    return TranslatorHub(
        {'ru': ('ru', 'en'), 'en': 'en'},
        [
            FluentTranslator(
                'ru',
                translator=FluentBundle.from_files('ru', filenames=[f'{DIR_PATH}/ru.ftl']),
            ),
            FluentTranslator(
                'en',
                translator=FluentBundle.from_files('en', filenames=[f'{DIR_PATH}/en.ftl']),
            ),
        ],
        root_locale='en',
    )
