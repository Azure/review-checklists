export interface TranslationResultSet {
    [to: string]: {
        [key: string]: string;
    }
}

export type TranslationResults = TranslationResult[];

export interface TranslationResult {
    detectedLanguage: DetectedLanguage;
    translations: Result[];
}

export interface DetectedLanguage {
    language: string;
    score: number;
}

export interface Result extends Record<string, string> {
    text: string;
    to: string;
}

// https://docs.microsoft.com/en-us/azure/cognitive-services/translator/quickstart-translate?pivots=programming-language-javascript#sample-response
// [
//     {
//         "detectedLanguage": {
//             "language": "en",
//             "score": 1.0
//         },
//         "translations": [
//             {
//                 "text": "Hallo Welt!",
//                 "to": "de"
//             },
//             {
//                 "text": "Salve, mondo!",
//                 "to": "it"
//             }
//         ]
//     }
// ]