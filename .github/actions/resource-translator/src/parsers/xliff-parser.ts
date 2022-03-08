import { traverseXliff, XliffFile, XliffFileKeyDelimiter } from "../file-formats/xliff-file";
import { TranslationFileParser } from "./translation-file-parser";
import { TranslatableTextMap } from "../abstractions/translatable-text-map";
import { XmlFileParser } from "./xml-file-parser";

export class XliffParser implements TranslationFileParser {
    async parseFrom(fileContent: string): Promise<XliffFile> {
        return await XmlFileParser.fromXml<XliffFile>(fileContent);
    }

    toFileFormatted(instance: XliffFile, defaultValue: string): string {
        try {
            return XmlFileParser.toXml(instance);
        } catch (error) {
            return defaultValue;
        }
    }

    applyTranslations(
        instance: XliffFile,
        translations: { [key: string]: string; } | undefined,
        targetLocale?: string): XliffFile {
        if (instance && translations && targetLocale) {
            instance.xliff.$.trgLang = targetLocale;
            for (let key in translations) {
                const compositeKey = key.split(XliffFileKeyDelimiter);
                const index = parseInt(compositeKey[0]);
                const sourceKey = compositeKey[1];
                const value = translations[key];
                if (value) {
                    traverseXliff(instance, index, sourceKey, s => s.target = [value]);
                }
            }
        }

        return instance;
    }

    toTranslatableTextMap(instance: XliffFile): TranslatableTextMap {
        const textToTranslate: Map<string, string> = new Map();
        for (let i = 0; i < instance.xliff.file.length; ++i) {
            const values = instance.xliff.file[i].unit;
            if (values && values.length) {
                for (let f = 0; f < values.length; ++f) {
                    const key = values[f].segment[0].source[0];
                    textToTranslate.set(`${i}${XliffFileKeyDelimiter}${key}`, key);
                }
            }
        }

        return {
            text: textToTranslate
        };
    }
}