import { debug, setFailed } from '@actions/core';
import Axios, { AxiosRequestConfig } from 'axios';
import { v4 } from 'uuid';
import { AvailableTranslations } from '../abstractions/available-translations';
import { TranslationResult, TranslationResults, TranslationResultSet } from '../abstractions/translation-results';
import { TranslatorResource } from '../abstractions/translator-resource';
import { toResultSet } from '../helpers/api-result-set-mapper';
import { batch, chunk } from '../helpers/utils';

/**
* https://docs.microsoft.com/azure/cognitive-services/translator/language-support#translate
*/
export const getAvailableTranslations = async (): Promise<AvailableTranslations> => {
    const apiUrl = 'https://api.cognitive.microsofttranslator.com/languages';
    const query = 'api-version=3.0&scope=translation';
    const response = await Axios.get<AvailableTranslations>(`${apiUrl}?${query}`);

    return response.data;
};

export const translate = async (
    translatorResource: TranslatorResource,
    toLocales: string[],
    translatableText: Map<string, string>,
    filePath: string): Promise<TranslationResultSet | undefined> => {
    try {
        // Current Azure Translator API rate limit
        // https://docs.microsoft.com/azure/cognitive-services/translator/request-limits#character-and-array-limits-per-request
        const apiRateLimit = 10000;
        const numberOfElementsLimit = 100;

        const validationErrors: string[] = [];
        translatableText.forEach((value, key) => {
            const valueStringifiedLength = JSON.stringify(value).length;
            if (valueStringifiedLength > apiRateLimit) {
                validationErrors.push(`Text for key '${key}' in file '${filePath}' is too long (${valueStringifiedLength}). Must be ${apiRateLimit} at most.`);
            }
        });
        if (validationErrors.length) {
            setFailed(validationErrors.join('\r\n'));
            return undefined;
        }

        const data = [...translatableText.values()].map(value => {
            return { text: value };
        });
        const headers = {
            'Ocp-Apim-Subscription-Key': translatorResource.subscriptionKey,
            'Content-type': 'application/json',
            'X-ClientTraceId': v4()
        };
        if (translatorResource.region) {
            headers['Ocp-Apim-Subscription-Region'] = translatorResource.region;
        }
        const options: AxiosRequestConfig = {
            method: 'POST',
            headers,
            data,
            responseType: 'json'
        };

        const baseUrl = translatorResource.endpoint.endsWith('/')
            ? translatorResource.endpoint
            : `${translatorResource.endpoint}/`;

        const characters = JSON.stringify(data).length;
        const batchedData = characters > apiRateLimit || data.length > numberOfElementsLimit
            ? batch(data, numberOfElementsLimit, apiRateLimit)
            : [data];

        let results: TranslationResults = [];
        for (let i = 0; i < batchedData.length; i++) {
            const batch = batchedData[i];
            const batchCharacters = JSON.stringify(batch).length;
            const localeCount = toLocales.length;
            const localesBatchSize = Math.floor(apiRateLimit / batchCharacters);
            const batchedLocales = localesBatchSize < localeCount
                ? chunk(toLocales, localesBatchSize)
                : [toLocales];

            for (let j = 0; j < batchedLocales.length; j++) {
                const locales = batchedLocales[j];
                const to = locales.map(to => `to=${to}`).join('&');
                debug(`Data batch ${i + 1}, Locales batch ${j + 1}, locales: ${to}`);

                const url = `${baseUrl}translate?api-version=3.0&${to}`;
                const response = await Axios.post<TranslationResult[]>(url, batch, options);
                const responseData = response.data;
                debug(`Data batch ${i + 1}, Locales batch ${j + 1}, response: ${JSON.stringify(responseData)}`);

                results = [...results, ...responseData];
            }
        }

        return toResultSet(results, toLocales, translatableText);
    } catch (ex) {
        // Try to write explicit error:
        // https://docs.microsoft.com/en-us/azure/cognitive-services/translator/reference/v3-0-reference#errors
        const e = ex.response
            && ex.response.data
            && ex.response.data as TranslationErrorResponse;
        if (e) {
            setFailed(`file: ${filePath}, error: { code: ${e.error.code}, message: '${e.error.message}' }}`);
        } else {
            setFailed(`Failed to translate input: file '${filePath}', ${ex}`);
        }

        return undefined;
    }
};

interface TranslationErrorResponse {
    error: {
        code: number,
        message: string;
    };
}