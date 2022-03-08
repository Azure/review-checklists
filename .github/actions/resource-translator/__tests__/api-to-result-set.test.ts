import { readFileSync } from 'fs';
import { resolve } from 'path';
import { toResultSet } from '../src/helpers/api-result-set-mapper';
import { TranslationResult, TranslationResults } from '../src/abstractions/translation-results';

const toLocales = [
    'af', 'ar', 'as', 'bg', 'bn', 'bs', 'ca', 'cs',
    'cy', 'da', 'de', 'el', 'es', 'et', 'fa',
    'fi', 'fil', 'fj', 'fr', 'ga', 'gu', 'he',
    'hi', 'hr', 'ht', 'hu', 'id', 'is', 'it', 'ja', 'kk',
    'kmr', 'kn', 'ko', 'ku', 'lt', 'lv', 'mg', 'mi', 'ml',
    'mr', 'ms', 'mt', 'mww', 'nb', 'nl', 'or', 'otq', 'pa',
    'pl', 'prs', 'ps', 'pt', 'ro', 'ru', 'sk',
    'sl', 'sm', 'sr-Cyrl', 'sr-Latn', 'sv', 'sw', 'ta',
    'te', 'th', 'tlh-Latn', 'tlh-Piqd', 'to', 'tr', 'ty',
    'uk', 'ur', 'vi', 'yua', 'yue', 'zh-Hans', 'zh-Hant'
];

test('API toResultSet: correctly maps results to set', async () => {
    const jsonPath = resolve(__dirname, './data/test.json');
    const json = readFileSync(jsonPath, 'utf-8');
    const results: TranslationResult[] = JSON.parse(json) as TranslationResults;

    const translatableText: Map<string, string> = new Map();
    translatableText.set("Greeting", "An amazing experience awaits.");
    translatableText.set("HelloWorld", "Hello, world!");
    translatableText.set("SurveyTitle", "How is Blazor working for you?");

    const actual = toResultSet(results, toLocales, translatableText);

    expect(actual).toBeTruthy();
    toLocales.forEach(locale => {
        expect(actual[locale]).toBeTruthy();
    });
});
