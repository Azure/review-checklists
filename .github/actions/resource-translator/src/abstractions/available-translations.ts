export interface AvailableTranslations {
    readonly translation: Translations;
}

export interface Translations {
    [locale: string]: Locale;
}

export interface Locale {
    name: string;
    nativeName: string;
    dir: string;
}