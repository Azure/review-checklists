import { TranslatableTextMap } from "../abstractions/translatable-text-map";
import { JsonFile } from "../file-formats/json-file";
import { TranslationFileParser } from "./translation-file-parser";

export class JsonParser implements TranslationFileParser {

    static DELIMITER: string = '[--]';

    parseFrom(fileContent: string): Promise<JsonFile> {
        const buildMap = (obj: any, parentPath?: string) => {
            for (const [key, value] of Object.entries(obj)) {
                const path = parentPath ? `${parentPath}${JsonParser.DELIMITER}${key}` : key;
                if (typeof value === "string") {
                    map.set(path, value);
                } else {
                    buildMap(value, path);
                }
            }
        };

        const map = new Map<string, string>();

        try {
            const content = JSON.parse(fileContent);
            buildMap(content);
        } catch (e) {
            throw new Error(`Failed to parse json. Error: ${e}. Content: ${fileContent}`);
        }

        return Promise.resolve(Object.fromEntries(map) as JsonFile);
    }

    toFileFormatted(instance: JsonFile, defaultValue: string): string {
        const content = {};

        const buildObject = (obj: any, keyParts: string[], value: string) => {
            const keyPart = keyParts[0];
            const isLastChild = keyParts.length === 1;
            obj[keyPart] = isLastChild ? value : obj[keyPart] ?? {};

            if (!isLastChild) {
                buildObject(obj[keyPart], keyParts.slice(1), value);
            }
        };

        for (const [key, value] of Object.entries(instance)) {
            const keyParts = key.split(JsonParser.DELIMITER);
            buildObject(content, keyParts, value);
        }

        return JSON.stringify(content, null, "\t");
    }

    applyTranslations(instance: JsonFile, translations: { [key: string]: string; } | undefined, targetLocale?: string): JsonFile {
        if (instance && translations) {
            for (let key in translations) {
                const value = translations[key];
                if (value) {
                    instance[key] = value;
                }
            }
        }

        return instance;
    }

    toTranslatableTextMap(instance: JsonFile): TranslatableTextMap {
        const textToTranslate: Map<string, string> = new Map();
        for (const [key, value] of Object.entries(instance)) {
            textToTranslate.set(key, value);
        }

        return {
            text: textToTranslate
        };
    }
}