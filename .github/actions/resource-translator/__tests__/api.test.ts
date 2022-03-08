import { setFailed } from "@actions/core";
import { existsSync } from 'fs';
import { resolve } from 'path';
import { Summary } from '../src/abstractions/summary';
import { getAvailableTranslations, translate } from '../src/api/translation-api';
import { ResourceFile } from '../src/file-formats/resource-file';
import { summarize } from '../src/helpers/summarizer';
import { getLocaleName, naturalLanguageCompare } from '../src/helpers/utils';
import { readFile } from '../src/io/reader-writer';
import { ResxParser } from '../src/parsers/resx-parser';

const expectedLocales = [
    'af', 'am', 'ar', 'as', 'az', 'bg', 'bn', 'bs', 'ca', 'cs',
    'cy', 'da', 'de', 'el', 'en', 'es', 'et', 'fa',
    'fi', 'fil', 'fj', 'fr', 'fr-CA', 'ga', 'gu', 'he',
    'hi', 'hr', 'ht', 'hu', 'hy', 'id', 'is', 'it', 'iu', 'ja', 'kk',
    'km', 'kmr', 'kn', 'ko', 'ku', 'lo', 'lt', 'lv', 'mg', 'mi', 'ml',
    'mr', 'ms', 'mt', 'mww', 'my', 'nb', 'ne', 'nl', 'or', 'otq', 'pa',
    'pl', 'prs', 'ps', 'pt', 'pt-PT', 'ro', 'ru', 'sk',
    'sl', 'sm', 'sq', 'sr-Cyrl', 'sr-Latn', 'sv', 'sw', 'ta',
    'te', 'th', 'ti', 'tlh-Latn', 'tlh-Piqd', 'to', 'tr', 'ty',
    'uk', 'ur', 'vi', 'yua', 'yue', 'zh-Hans', 'zh-Hant'
];

const parser = new ResxParser();

jest.setTimeout(60000);
jest.useFakeTimers();
jest.mock('@actions/core');

test('API: translate fails to process too long text', async () => {
    const longTextLength = 10 * 1000;
    const resourceXml: ResourceFile = {
        root: {
            data: [
                { $: { name: 'Key1' }, value: ['a'.repeat(longTextLength)] },
                { $: { name: 'Key2' }, value: ['b'.repeat(longTextLength)] }
            ]
        }
    };

    const filePath = 'file-path';
    const expectedError = resourceXml.root.data
        .map(data => `Text for key '${data.$.name}' in file '${filePath}' is too long (${longTextLength + 2}). Must be ${longTextLength} at most.`)
        .join('\r\n');

    const translatableTextMap = parser.toTranslatableTextMap(resourceXml);
    const translatorResource = {
        endpoint: '',
        subscriptionKey: ''
    };
    const resultSet = await translate(
        translatorResource,
        [],
        translatableTextMap.text,
        filePath);

    expect(resultSet).toBeUndefined();
    const setFailedMock = setFailed as jest.MockedFunction<typeof setFailed>;
    expect(setFailedMock).toBeCalledWith(expectedError);
});

test('API: get available translations correctly gets all locales', async () => {
    const translations = await getAvailableTranslations();

    expect(translations).toBeTruthy();

    const locales = Object.keys(translations.translation);    
    expect(locales.some(locale => expectedLocales.includes(locale))).toBeTruthy();
});

test.skip('API: read file->translate->apply->write', async () => {
    const availableTranslations = await getAvailableTranslations();
    const sourceLocale = 'en';
    const toLocales =
        Object.keys(availableTranslations.translation)
            .filter(locale => locale !== sourceLocale)
            .sort((a, b) => naturalLanguageCompare(a, b));

    const filePath = './data/UIStrings.en.resx';
    const resourceFiles = [resolve(__dirname, filePath)];
    let summary = new Summary(sourceLocale, toLocales);

    for (let index = 0; index < resourceFiles.length; ++index) {
        const resourceFilePath = resourceFiles[index];
        const resourceFileXml = readFile(resourceFilePath);
        const file = await parser.parseFrom(resourceFileXml);
        const translatableTextMap = parser.toTranslatableTextMap(file);

        if (translatableTextMap) {
            const resultSet = await translate(
                {
                    endpoint: process.env['AZURE_TRANSLATOR_ENDPOINT'] || 'https://api.cognitive.microsofttranslator.com/',
                    subscriptionKey: process.env['AZURE_TRANSLATOR_SUBSCRIPTION_KEY'] || 'unknown!',
                    region: process.env['AZURE_TRANSLATOR_SUBSCRIPTION_REGION'] || undefined
                },
                toLocales,
                translatableTextMap.text,
                filePath);

            if (resultSet) {
                const length = translatableTextMap.text.size;
                toLocales.forEach(locale => {
                    const translations = resultSet[locale];
                    const clone = Object.assign({} as ResourceFile, file);
                    const result = parser.applyTranslations(clone, translations);
                    const translatedXml = parser.toFileFormatted(result, "");
                    const newPath = getLocaleName(resourceFilePath, locale);
                    if (translatedXml && newPath) {
                        if (existsSync(newPath)) {
                            summary.updatedFileCount++;
                            summary.updatedFileTranslations += length;
                        } else {
                            summary.newFileCount++;
                            summary.newFileTranslations += length;
                        }
                        // writeFile(newPath, translatedXml);
                    }
                });
            }
        }
    }

    const [title, details] = summarize(summary);
    expect(title).toEqual('Machine-translated 89 files, a total of 1,335 translations');
    expect(details).toBeTruthy();
});

test.skip('API: translate correctly performs translation', async () => {
    const resourceXml: ResourceFile = {
        root: {
            data: [
                { $: { name: 'Greeting' }, value: ['Welcome to your new app'] },
                { $: { name: 'HelloWorld' }, value: ['Hello, world!'] },
                { $: { name: 'SurveyTitle' }, value: ['How is Blazor working for you? Testing...'] }
            ]
        }
    };
    const translatableTextMap = parser.toTranslatableTextMap(resourceXml);
    const translatorResource = {
        endpoint: process.env['AZURE_TRANSLATOR_ENDPOINT'] || 'https://api.cognitive.microsofttranslator.com/',
        subscriptionKey: process.env['AZURE_TRANSLATOR_SUBSCRIPTION_KEY'] || 'unknown!',
        region: process.env['AZURE_TRANSLATOR_SUBSCRIPTION_REGION'] || undefined
    };
    const resultSet = await translate(
        translatorResource,
        ['fr', 'es'],
        translatableTextMap.text,
        'file-path');

    expect(resultSet).toEqual(
        {
            'es': {
                'Greeting': 'Bienvenido a su nueva aplicación',
                'HelloWorld': '¡Hola mundo!',
                'SurveyTitle': '¿Cómo funciona Blazor para ti? Pruebas...'
            },
            'fr': {
                'Greeting': 'Bienvenue dans votre nouvelle application',
                'HelloWorld': 'Salut tout le monde!',
                'SurveyTitle': 'Comment Blazor travaille-t-il pour vous ? Test...'
            }
        });
});
