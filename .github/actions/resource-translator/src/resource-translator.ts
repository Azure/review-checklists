import { debug, info, setFailed, setOutput } from '@actions/core';
import { existsSync } from 'fs';
import { Summary } from './abstractions/summary';
import { TranslationFileKind } from './abstractions/translation-file-kind';
import { Inputs } from './action/inputs';
import { getAvailableTranslations, translate } from './api/translation-api';
import { translationFileParserFactory } from './factories/translation-file-parser-factory';
import { TranslationFile } from './file-formats/translation-file';
import { summarize } from './helpers/summarizer';
import { getLocaleName, naturalLanguageCompare, stringifyMap } from './helpers/utils';
import { readFile, writeFile } from './io/reader-writer';
import { findAllTranslationFiles } from './io/translation-file-finder';

export async function start(inputs: Inputs) {
    try {
        if (!inputs) {
            setFailed('Both a subscriptionKey and endpoint are required.');
        } else {
            const availableTranslations = await getAvailableTranslations();
            if (!availableTranslations || !availableTranslations.translation) {
                setFailed("Unable to get target translations.");
                return;
            }
            const sourceLocale = inputs.sourceLocale;
            const toLocales =
                Object.keys(availableTranslations.translation)
                    .filter(locale => {
                        if (locale === sourceLocale) {
                            return false;
                        }

                        if (inputs.toLocales && inputs.toLocales.length) {
                            return inputs.toLocales.some(l => l === locale);
                        }

                        return true;
                    })
                    .sort((a, b) => naturalLanguageCompare(a, b));
            info(`Detected translation targets to: ${toLocales.join(", ")}`);

            const translationFiles = await findAllTranslationFiles(inputs.sourceLocale);
            if (!translationFiles ||
                (!translationFiles.po &&
                    !translationFiles.restext &&
                    !translationFiles.resx &&
                    !translationFiles.xliff &&
                    !translationFiles.ini &&
                    !translationFiles.json)) {
                setFailed("Unable to get target resource files.");
                return;
            }

            let summary = new Summary(sourceLocale, toLocales);

            for (let key of Object.keys(translationFiles)) {
                debug(`Iterating translationFiles keys, key: ${key}`);
                
                const kind = key as TranslationFileKind;
                const files = translationFiles[kind];
                if (!files || !files.length) {
                    debug(`For kind ${kind}, there are no translation files.`);
                    continue;
                }

                debug(`Translation file parser kind: ${kind}`);

                const translationFileParser = translationFileParserFactory(kind);
                for (let index = 0; index < files.length; ++index) {
                    const filePath = files[index];
                    const fileContent = readFile(filePath);
                    const parsedFile = await translationFileParser.parseFrom(fileContent);
                    const translatableTextMap = translationFileParser.toTranslatableTextMap(parsedFile);

                    debug(`Translatable text:\n ${JSON.stringify(translatableTextMap, stringifyMap)}`);

                    if (translatableTextMap) {
                        const resultSet = await translate(
                            inputs,
                            toLocales,
                            translatableTextMap.text,
                            filePath);

                        debug(`Translation result:\n ${JSON.stringify(resultSet)}`);

                        if (resultSet !== undefined) {
                            const length = translatableTextMap.text.size;
                            debug(`Translation count: ${length}, toLocales size: ${toLocales.length}`);

                            for (let i = 0; i < toLocales.length; ++ i) {
                                const locale = toLocales[i];
                                const translations = resultSet[locale];
                                if (translations) {
                                    const clone = Object.assign({} as TranslationFile, parsedFile);
                                    const result =
                                        translationFileParser.applyTranslations(
                                            clone, translations, locale);

                                    const translatedFile = translationFileParser.toFileFormatted(result, "");
                                    const newPath = getLocaleName(filePath, locale);
                                    if (translatedFile && newPath) {
                                        debug(`The newPath: ${newPath}`);
                                        
                                        if (existsSync(newPath)) {
                                            summary.updatedFileCount++;
                                            summary.updatedFileTranslations += length;
                                        } else {
                                            summary.newFileCount++;
                                            summary.newFileTranslations += length;
                                        }
                                        writeFile(newPath, translatedFile);
                                    } else {
                                        debug(`The translatedFile value is ${translatedFile}`);
                                        debug(`The newPath would have been ${newPath}`);
                                    }
                                } else  {
                                    debug(`Unable to find resulting translations for: ${locale}`);
                                }
                            }
                        } else {
                            setFailed("Unable to translate input text.");
                        }
                    } else {
                        setFailed("No translatable text to work with");
                    }
                }
            }

            setOutput('has-new-translations', summary.hasNewTranslations);

            const [title, details] = summarize(summary);
            setOutput('summary-title', title);
            setOutput('summary-details', details);
        }
    } catch (error) {
        console.trace();
        setFailed(error.message);
    }
}